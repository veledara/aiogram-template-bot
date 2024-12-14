from pydantic import SecretStr, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: SecretStr
    user_agreement_url: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def __init__(self, **values):
        super().__init__(**values)


settings = Settings()
