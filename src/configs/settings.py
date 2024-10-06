import os
import re
from typing import Optional

from arq.connections import RedisSettings
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Общие настройки"""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        secrets_dir=os.getenv("SECRETS_ADDRESS"),
        extra="allow"
    )

    TOKEN: str
    SECRETS_ADDRESS: Optional[str] = None
    ADMINS: str
    TEST_DATA: bool
    STAFF_CLIENT_ID: str
    STAFF_CLIENT_SECRET: str

    @field_validator("ADMINS")
    def check_admin_emails(cls, emails: str) -> str:
        result = True
        for email in emails.split():
            if not re.search(r"^.*@((skbkontur)|(kontur))\.\w+$", email):
                result = False
        if not result:
            raise ValueError("В переменной среды Admins должны быть контуровские почты админов")
        else:
            return emails


class RedisConfig(BaseSettings):
    REDIS_DB: int
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        secrets_dir=os.getenv("SECRETS_ADDRESS"),
        extra="allow"
    )

    def get_connection_str(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_pool_settings(self) -> RedisSettings:
        return RedisSettings(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            database=self.REDIS_DB,
        )

class PGSettings(BaseSettings):
    """Настройки для подключения к БД"""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        secrets_dir=os.getenv("SECRETS_ADDRESS"),
        extra="allow"
    )

    PG_USER: str
    PG_PASS: str
    POSTGRES_URL: str
    PG_DB_NAME: str

    def db_connection_sync(self) -> str:
        return f"postgresql+psycopg2://{self.PG_USER}:{self.PG_PASS}@{self.POSTGRES_URL}/{self.PG_DB_NAME}"

    def db_connection_async(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.POSTGRES_URL}/{self.PG_DB_NAME}"
