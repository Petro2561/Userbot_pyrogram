import sys
import logging
import asyncio

from bot import bot, check_and_send_messages
from models.db import async_main
from config import load_config
from pyrogram import idle


async def main():
    config = load_config()
    await async_main()
    user_bot = bot(api_id=config.user_bot.api_id, api_hash=config.user_bot.api_hash)
    await user_bot.start()
    asyncio.create_task(check_and_send_messages(user_bot))
    await idle()
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')