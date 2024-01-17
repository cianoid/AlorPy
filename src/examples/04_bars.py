import os.path
from datetime import datetime, timedelta
from time import time

import pandas as pd

from src.alor import Alor  # Работа с Alor OpenAPI V2
from src.config import settings  # Файл конфигурации


def save_candles_to_file(
    ap_provider=Alor(settings.user_name, settings.refresh_token),
    exchange="MOEX",
    board="TQBR",
    symbols=("SBER",),
    time_frame="D",
    datapath=os.path.join("..", "..", "DataAlor", ""),
    skip_first_date=False,
    skip_last_date=False,
    four_price_doji=False,
):
    """Получение баров, объединение с имеющимися барами в файле (если есть), сохранение баров в файл

    :param Alor ap_provider: Провайдер Alor
    :param str exchange: Биржа 'MOEX' или 'SPBX'
    :param str board: Код площадки
    :param tuple symbols: Коды тикеров в виде кортежа
    :param int|str time_frame: Временной интервал в секундах (int) или код ("D" - дни, "W" - недели, "M" - месяцы,
    "Y" - годы)
    :param str datapath: Путь сохранения файла '..\\..\\DataAlor\\' - Windows, '../../DataAlor/' - Linux
    :param bool skip_first_date: Убрать бары на первую полученную дату
    :param bool skip_last_date: Убрать бары на последнюю полученную дату
    :param bool four_price_doji: Оставить бары с дожи 4-х цен
    """
    tf = (
        f"{time_frame}1"
        if time_frame in ("D", "W", "Y")
        else "MN1"
        if time_frame == "M"
        else f"M{int(time_frame) // 60}"
    )  # Временной интервал для файла
    intraday = tf != "MN1" and tf.startswith("M")  # Внутридневные интервалы начинаются с M, кроме MN1 (месяц)
    for symbol in symbols:  # Пробегаемся по всем тикерам
        file_bars = None  # Дальше будем пытаться получить бары из файла
        file_name = f"{datapath}{board}.{symbol}_{tf}.txt"
        file_exists = os.path.isfile(file_name)  # Существует ли файл
        if file_exists:  # Если файл существует
            print(f"Получение файла {file_name}")
            file_bars = pd.read_csv(
                file_name, sep="\t", parse_dates=["datetime"], date_format="%d.%m.%Y %H:%M", index_col="datetime"
            )  # Считываем файл в DataFrame
            last_date: datetime = file_bars.index[-1]  # Дата и время последнего бара
            print(f"- Первая запись файла: {file_bars.index[0]}")
            print(f"- Последняя запись файла: {last_date}")
            print(f"- Кол-во записей в файле: {len(file_bars)}")
            seconds_from = (
                ap_provider.msk_datetime_to_utc_timestamp(last_date + timedelta(seconds=1))
                if intraday
                else ap_provider.msk_datetime_to_utc_timestamp(last_date + timedelta(days=1))
            )  # Смещаем время на возможный следующий бар по UTC
        else:  # Файл не существует
            print(f"Файл {file_name} не найден и будет создан")
            seconds_from = 0  # Берем отметку времени, когда никакой тикер еще не торговался
        print(f"Получение истории {board}.{symbol} {tf} из Alor")
        new_bars = ap_provider.get_history(exchange, symbol, time_frame, seconds_from)[
            "history"
        ]  # Получаем все бары из Alor
        if len(new_bars) == 0:  # Если новых бар нет
            print("Новых записей нет")
            continue  # то переходим к следующему тикеру, дальше не продолжаем
        pd_bars = pd.json_normalize(new_bars)  # Переводим список баров в pandas DataFrame
        pd_bars["datetime"] = pd.to_datetime(pd_bars["time"], unit="s")  # Дата и время в UTC для дневных бар и выше
        si = ap_provider.get_symbol(exchange, symbol)  # Получаем информацию о тикере
        pd_bars["volume"] *= si["lotsize"]  # Объемы из лотов переводим в штуки
        if type(time_frame) is not str:  # Для внутридневных баров (time_frame число)
            pd_bars["datetime"] = (
                pd_bars["datetime"].dt.tz_localize("UTC").dt.tz_convert(ap_provider.tz_msk).dt.tz_localize(None)
            )  # Переводим в рыночное время МСК
        pd_bars.index = pd_bars["datetime"]  # Это будет индексом
        pd_bars = pd_bars[
            ["datetime", "open", "high", "low", "close", "volume"]
        ]  # Отбираем нужные колонки. Дата и время нужна, чтобы не удалять одинаковые OHLCV на разное время
        pd_bars.volume = pd.to_numeric(pd_bars.volume, downcast="integer")  # Объемы могут быть только целыми
        if not file_exists and skip_first_date:  # Если файла нет, и убираем бары на первую дату
            len_with_first_date = len(pd_bars)  # Кол-во баров до удаления на первую дату
            first_date = pd_bars.index[0].date()  # Первая дата
            pd_bars.drop(pd_bars[(pd_bars.index.date == first_date)].index, inplace=True)  # Удаляем их
            print(f"- Удалено баров на первую дату {first_date}: {len_with_first_date - len(pd_bars)}")
        if skip_last_date:  # Если убираем бары на последнюю дату
            len_with_last_date = len(pd_bars)  # Кол-во баров до удаления на последнюю дату
            last_date = pd_bars.index[-1].date()  # Последняя дата
            pd_bars.drop(pd_bars[(pd_bars.index.date == last_date)].index, inplace=True)  # Удаляем их
            print(f"- Удалено баров на последнюю дату {last_date}: {len_with_last_date - len(pd_bars)}")
        if not four_price_doji:  # Если удаляем дожи 4-х цен
            len_with_doji = len(pd_bars)  # Кол-во баров до удаления дожи
            pd_bars.drop(
                pd_bars[(pd_bars.high == pd_bars.low)].index, inplace=True
            )  # Удаляем их по условия High == Low
            print("- Удалено дожи 4-х цен:", len_with_doji - len(pd_bars))
        if len(pd_bars) == 0:  # Если нечего объединять
            print("Новых записей нет")
            continue  # то переходим к следующему тикеру, дальше не продолжаем
        print(f"- Первая запись в Alor: {pd_bars.index[0]}")
        print(f"- Последняя запись в Alor: {pd_bars.index[-1]}")
        print(f"- Кол-во записей в Alor: {len(pd_bars)}")
        if file_exists:  # Если файл существует
            pd_bars = (
                pd.concat([file_bars, pd_bars]).drop_duplicates(keep="last").sort_index()
            )  # Объединяем файл с данными из Alor, убираем дубликаты, сортируем заново
        pd_bars = pd_bars[
            ["open", "high", "low", "close", "volume"]
        ]  # Отбираем нужные колонки. Дата и время будет экспортирована как индекс
        pd_bars.to_csv(file_name, sep="\t", date_format="%d.%m.%Y %H:%M")
        print(f"- В файл {file_name} сохранено записей: {len(pd_bars)}")


if __name__ == "__main__":  # Точка входа при запуске этого скрипта
    start_time = time()  # Время начала запуска скрипта

    board = "TQBR"  # Акции ММВБ
    # board = 'SPBFUT'  # Фьючерсы
    symbols = (
        "SBER",
        "VTBR",
        "GAZP",
        "MTLR",
        "LKOH",
        "PLZL",
        "SBERP",
        "BSPB",
        "POLY",
        "RNFT",
        "GMKN",
        "AFLT",
        "NVTK",
        "TATN",
        "YNDX",
        "MGNT",
        "ROSN",
        "AFKS",
        "NLMK",
        "ALRS",
        "MOEX",
        "SMLT",
        "MAGN",
        "CHMF",
        "CBOM",
        "MTLRP",
        "SNGS",
        "BANEP",
        "MTSS",
        "IRAO",
        "SNGSP",
        "SELG",
        "UPRO",
        "RUAL",
        "TRNFP",
        "FEES",
        "SGZH",
        "BANE",
        "PHOR",
        "PIKK",
    )  # TOP 40 акций ММВБ
    # symbols = ('SBER',)  # Для тестов
    # Формат фьючерса: <Тикер><Месяц экспирации><Последняя цифра года> Месяц экспирации: 3-H, 6-M, 9-U, 12-Z
    # symbols = ('SiZ3', 'RIZ3')

    skip_last_date = True  # Если получаем данные внутри сессии, то не берем бары за дату незавершенной сессии
    # skip_last_date = False  # Если получаем данные, когда рынок не работает, то берем все бары
    save_candles_to_file(
        board=board, symbols=symbols, skip_last_date=skip_last_date, four_price_doji=True
    )  # Получаем дневные бары (с начала)
    # Получаем часовые бары (с 11.12.2017)
    # save_candles_to_file(board=board, symbols=symbols, time_frame=3600, skip_last_date=skip_last_date)
    # Получаем 15-и минутные бары (с 11.12.2017)
    # save_candles_to_file(board=board, symbols=symbols, time_frame=900, skip_last_date=skip_last_date)
    # Получаем 5-и минутные бары (с 11.12.2017)
    # save_candles_to_file(board=board, symbols=symbols, time_frame=300, skip_last_date=skip_last_date)
    # Получаем минутные бары (с 11.12.2007)
    # save_candles_to_file(board=board, symbols=symbols, time_frame=60, skip_last_date=skip_last_date,
    # four_price_doji=True)

    print(f"Скрипт выполнен за {(time() - start_time):.2f} с")
