from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    admin_list: list[int]
    log_level: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
