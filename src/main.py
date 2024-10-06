import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from adapters import dbhelper
from configs.settings import CommonSettings
from tg import auth, main_screen


async def start_bot(token: str) -> None:
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(auth.router, main_screen.router)
    await bot.set_my_commands([BotCommand(command="/all", description="Весь список устройств")])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main() -> None:
    await dbhelper.start_db_async()
    await start_bot(CommonSettings().TOKEN)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    asyncio.run(main())
