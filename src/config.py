from dataclasses import dataclass

from environs import Env
from sqlalchemy import URL


@dataclass
class DatabaseConfig:
    db: str


@dataclass
class UserBot:
    api_id: str
    api_hash: str


@dataclass
class Config:
    user_bot: UserBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        user_bot=UserBot(api_id=env("API_ID"), api_hash=env("API_HASH")),
        db=DatabaseConfig(
            db=env("DATABASE_URL"),
        ),
    )
