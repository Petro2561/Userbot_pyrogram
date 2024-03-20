import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client, errors
from pyrogram.types import Message
from sqlalchemy import select

from models.db import User, async_session

logger = logging.getLogger(__name__)

FIRST_TEXT = "Первый текст"
SECOND_TEXT = "Второй текст"
TFIRD_TEXT = "Третий текст"
FIRST_TEXT_TIME = 6
SECOND_TEXT_TIME = 36
THIRD_TEXT_TIME = 60 * 26
SCENARIO = {
    FIRST_TEXT_TIME: FIRST_TEXT,
    SECOND_TEXT_TIME: SECOND_TEXT,
    THIRD_TEXT_TIME: TFIRD_TEXT,
}
LAST_MESSAGE_DELAY = sorted(SCENARIO.keys())[-1]
TRIGERS = ("прекрасно", "ожидать")
ALIVE_STATUS = "alive"
DEAD_STATUS = "dead"
FINISHED_STATUS = "finished"
BLOCKED_MESSAGE = "Юзербот был заблокирован пользователем {user_id}."
DEACTIVATED_MESSAGE = "Пользователь {user_id} некативен."
ERROR_MESSAGE = "Ошибка отправки сообщения{user_id}: {error}"
RECEIVED_MESSAGE_LOG = "Получено сообщение от {}: {}"

logger = logging.getLogger(__name__)


async def handle_message(client: Client, message: Message):
    """Хэндлер для обработки сообщений"""
    async with async_session() as session:
        async with session.begin():
            user_id = message.from_user.id
            logger.info(RECEIVED_MESSAGE_LOG.format(user_id, message.text))
            user = await get_or_create_user(user_id, session)
            user.status_updated_at = datetime.now()
            if not await check_message_for_triggers(message.text):
                user.status = FINISHED_STATUS
            await session.commit()


async def check_and_send_messages(client: Client):
    """Цикл проверки сообщений. Каждую минуту проверяет не наступил ли следующий этап воронки."""
    while True:
        async with async_session() as session:
            current_time = datetime.now()
            async with session.begin():
                result = await session.execute(
                    select(User).where(
                        User.status == ALIVE_STATUS,
                    )
                )
                users_to_notify = result.scalars().all()
                for user in users_to_notify:
                    await send_sales_message(client, user, current_time)
                await session.commit()
        await asyncio.sleep(60)


async def send_sales_message(client: Client, user: User, current_time: datetime):
    """Функция для проверки времени воронки"""
    for delay_minutes, message_text in SCENARIO.items():
        delay_time = user.created_at + timedelta(minutes=delay_minutes)
        if user.last_message_sent < delay_minutes and current_time >= delay_time:
            await send_message_safe(client=client, user_id=user.id, text=message_text)
            user.last_message_sent = delay_minutes
            if delay_minutes == LAST_MESSAGE_DELAY:
                user.status = FINISHED_STATUS
            break


async def get_or_create_user(user_id, session):
    """Функция создания юзера"""
    user = await session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            created_at=datetime.now(),
            status=ALIVE_STATUS,
            status_updated_at=datetime.now(),
        )
        session.add(user)
    return user


async def send_message_safe(client: Client, user_id: int, text: str):
    """Функция отправки сообщений"""
    async with async_session() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            try:
                await client.send_message(user_id, text)
            except errors.UserIsBlocked:
                logger.info(BLOCKED_MESSAGE.format(user_id=user_id))
                user.status = DEAD_STATUS
            except errors.UserDeactivated:
                logger.info(DEACTIVATED_MESSAGE.format(user_id=user_id))
                user.status = DEAD_STATUS
            except Exception as error:
                logger.error(ERROR_MESSAGE.format(user_id=user_id, error=error))
            finally:
                await session.commit()


async def check_message_for_triggers(message_text: str):
    """Проверка сообщений на триггер"""
    triggers = TRIGERS
    if any(trigger in message_text.lower() for trigger in triggers):
        return False
    else:
        return True
