import asyncio
import os

from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from contextlib import suppress
from aiogram import Bot, Dispatcher

from bot.handlers import message_handlers, callbacks
from bot.database.db_utils import start_db, close_db
from bot.utils import logging_config


async def main() -> None:
    logging_config.configure_logging()

    load_dotenv()
    bot = Bot(os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(start_db)
    dp.shutdown.register(close_db)

    dp.include_router(message_handlers.router)
    dp.include_router(callbacks.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
