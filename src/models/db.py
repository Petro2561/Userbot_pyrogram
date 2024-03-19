from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from config import load_config

config = load_config()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Enum('alive', 'dead', 'finished', name='user_status'), default='alive')
    status_updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    last_message_time = Column(DateTime, default=None)

engine = create_async_engine(config.db.db)

async_session = async_sessionmaker(engine, class_=AsyncSession)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
