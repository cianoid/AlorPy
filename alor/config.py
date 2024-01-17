from pydantic_settings import BaseSettings, SettingsConfigDict

# Чтобы получить Refresh Token:
# 0. Для получения тестового логина/пароля демо счета оставить заявку в Telegram на https://t.me/AlorOpenAPI
# 1. Зарегистрироваться на https://alor.dev/login
# 2. Выбрать "Токены для доступа к API"

# Для реального счета:
# 1. Привязать торговый аккаунт
# 2. Выписать токен

# Для демо счета:
# 1. Пройти по ссылке "Токены для ведения торгов в тестовом контуре" - "Begin OAuth authorization flow"
# 2. Ввести тестовый логин/пароль. Нажать "Разрешить"

# Как заполнять переменные портфелей PortfolioStocks, PortfolioFutures, PortfolioFx:
# 1. Запустить скрипт "Examples/02 - Accounts.py"
# 2. Получить портфели для всех рынков
# 3. Заполнить переменные полученными значениями

# Коды торговых серверов для стоп заявок:
TradeServerCode = "TRADE"  # Рынок Ценных Бумаг
ITradeServerCode = "ITRADE"  # Рынок Иностранных Ценных Бумаг
FutServerCode = "FUT1"  # Фьючерсы
OptServerCode = "OPT1"  # Опционы
FxServerCode = "FX1"  # Валютный рынок


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env",), extra="ignore")
    # Имя пользователя
    user_name: str = ""
    # Токен
    refresh_token: str = ""

    # Портфель фондового рынка
    portfolio_stocks: str = "D00000"
    # Портфель срочного рынка
    portfolio_futures: str = "0000PST"
    # Портфель валютного рынка
    portfolio_fx: str = "G00000"

    # Привязка портфелей к биржам
    accounts: dict = {}
    # Привязка портфелей/серверов для стоп заявок к площадкам
    boards: dict = {}

    # Тикер
    ticker: str
    # сколько кэша на портфеле
    cash: float
    # Размер заявки
    order_size: int
    # Комиссия
    commission: float
    stop_loss_percent: float

    log_level: str = "DEBUG"
    title: str = "Strategies"

    def __init__(self):
        super().__init__()

        self.accounts = {
            # Фондовый рынок на Московской Бирже (RUB) и СПб Бирже (USD)
            self.portfolio_stocks: (
                "MOEX",
                "SPBX",
            ),
            # Срочный рынок на Московской Бирже (RUB)
            self.portfolio_futures: ("MOEX",),
            # Валютный рынок на Московской Бирже (RUB)
            self.portfolio_fx: ("MOEX",),
        }
        self.boards = {
            "TQBR": (self.portfolio_stocks, TradeServerCode),  # Т+ Акции и ДР
            "TQOB": (self.portfolio_stocks, TradeServerCode),  # МБ ФР: Т+: Гособлигации
            "TQCB": (self.portfolio_stocks, TradeServerCode),  # МБ ФР: Т+: Облигации
            "RFUD": (self.portfolio_stocks, FutServerCode),  # FORTS: Фьючерсы
        }


settings = Settings()
