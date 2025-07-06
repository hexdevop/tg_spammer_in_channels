from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class BotSettings(BaseModel):
    token: str
    error_notification: int  # 0 - off, 1 - to admins, 2 - to developer
    skip_updates: bool


class DatabaseSettings(BaseModel):
    host: str
    user: str
    password: str
    database: str

    @property
    def database_url(self):
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}/{self.database}"

class RedisSettings(BaseModel):
    host: str
    states: int
    jobs: int
    cache: int


class Config(BaseSettings):
    bot: BotSettings
    database: DatabaseSettings
    redis: RedisSettings

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


config = Config()  # noqa
