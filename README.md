# Alor
Библиотека-обертка, которая позволяет работать с функционалом [Alor OpenAPI V2](https://alor.dev/docs) брокера [Алор](https://www.alorbroker.ru/) (далее OpenAPI) из Python.

## Для чего нужна
С помощью этой библиотеки можно создавать автоматические торговые системы любой сложности на Python для OpenAPI. Также библиотека может быть использована для написания дополнений на Python к системам Технического Анализа. Например, для тестирования и автоматической торговли в [BackTrader](https://www.backtrader.com/).

## Установка коннектора
1. Установите все требуемые библиотеки через **pip install -r requirements.txt**
2. Чтобы получить Refresh Token:
   * Для получения тестового логина/пароля демо счета оставить заявку в Telegram на https://t.me/AlorOpenAPI
   * Зарегистрироваться на https://alor.dev/login
   * Выбрать "Токены для доступа к API"
3. Для реального счета:
   * Привязать торговый аккаунт
   * Выписать токен
4. Для демо счета:
   * Пройти по ссылке "Токены для ведения торгов в тестовом контуре" - "Begin OAuth authorization flow"
   * Ввести тестовый логин/пароль. Нажать "Разрешить"


## Авторство, право использования, развитие
Автор данной библиотеки Чечет Игорь Александрович.

Библиотека написана в рамках проекта [Финансовая Лаборатория](https://finlab.vip/) и предоставляется бесплатно. При распространении ссылка на автора и проект обязательны.
