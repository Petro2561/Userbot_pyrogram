import asyncio
import logging
import sys

from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from bot import check_and_send_messages, handle_message
from config import load_config
from models.db import async_main


async def main():
    config = load_config()
    await async_main()
    user_bot = Client(
        "my_user_bot", api_id=config.user_bot.api_id, api_hash=config.user_bot.api_hash
    )
    user_bot.add_handler(MessageHandler(handle_message, filters.text & filters.private))
    await user_bot.start()
    asyncio.create_task(check_and_send_messages(user_bot))
    await idle()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
