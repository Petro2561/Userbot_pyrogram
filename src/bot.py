import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, errors
from sqlalchemy import select
from models.db import async_session, User  # Предполагается, что async_session это ваша асинхронная сессия из SQLAlchemy
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

FIRST_TEXT = 'Первый текст'
SECOND_TEXT = 'Второй текст'
TFIRD_TEXT = 'Третий текст'
FIRST_TEXT_TIME = 1
SECOND_TEXT_TIME = 2
THIRD_TEXT_TIME = 3
SCENARIO = {
    FIRST_TEXT_TIME: FIRST_TEXT,
    SECOND_TEXT_TIME: SECOND_TEXT,
    THIRD_TEXT_TIME: TFIRD_TEXT,
}
TRIGERS = ("прекрасно", "ожидать")

logger = logging.getLogger(__name__)

async def handle_message(client: Client, message: Message):
    async with async_session() as session:
        async with session.begin():
            user_id = message.from_user.id
            logger.info(f"Получено сообщение от {user_id}: {message.text}")
            user = await get_or_create_user(user_id, session)
            user.status_updated_at = datetime.now()
            if not await check_message_for_triggers(message.text):
                user.status = 'finished'
            await session.commit()


async def check_and_send_messages(client: Client):
    while True:
        async with async_session() as session:
            current_time = datetime.now()
            async with session.begin():
                result = await session.execute(
                    select(User).where(
                        User.status == 'alive',
                    )
                )
                users_to_notify = result.scalars().all()
                for user in users_to_notify:
                    await send_sales_message(client, user, current_time)
                
                await session.commit()
        await asyncio.sleep(60)

async def send_sales_message(client: Client, user: User, current_time: datetime):
    for delay_minutes, message_text in SCENARIO.items():
        delay_time = user.created_at + timedelta(minutes=delay_minutes)
        if user.last_message_sent < delay_minutes and current_time >= delay_time:
            await send_message_safe(client=client, chat_id=user.id, text=message_text)
            user.last_message_sent = delay_minutes
            break


async def get_or_create_user(user_id, session):
    user = await session.get(User, user_id)
    if not user:
        user = User(id=user_id, created_at=datetime.now(), status='alive', status_updated_at=datetime.now())
        session.add(user)
        logger.info(f"Создан новый пользователь с ID {user_id}")
    return user 

async def send_message_safe(client: Client, user_id: int, text: str):
    async with async_session() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            try:
                await client.send_message(user_id, text)
            except errors.UserIsBlocked:
                logger.info(f"Юзербот был заблокирован пользователем {user_id}.")
                user.status = 'dead'
            except errors.UserDeactivated:
                logger.info(f"Пользователь {user_id} некативен.")
                user.status = 'dead'
            except Exception as error:
                logger.error(f"Ошибка отправки сообщения{user_id}: {error}")
            finally:
                await session.commit() 

async def check_message_for_triggers(message_text: str):
    triggers = TRIGERS
    if any(trigger in message_text.lower() for trigger in triggers):
        return False
    else: 
        return True

def bot(api_id, api_hash):
    app = Client("my_user_bot", api_id=api_id, api_hash=api_hash)
    app.add_handler(MessageHandler(handle_message, filters.text & filters.private))
    return app
