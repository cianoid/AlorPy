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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env",), extra="ignore")
    # Токен
    refresh_token: str = ""

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


settings = Settings()
