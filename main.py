import asyncio
import json
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from yt_dlp import YoutubeDL

from bot_commands import BOT_COMMANDS
from middlewares import AdminMiddleware
from settings import Settings
from handlers import router

def register_middlewares(dispatcher: Dispatcher, settings: Settings):
    dispatcher.message.outer_middleware(AdminMiddleware(settings.admin_list))
    dispatcher.callback_query.outer_middleware(AdminMiddleware(settings.admin_list))


async def main() -> None:
    settings = Settings()
    
    logging.basicConfig(level=settings.log_level, stream=sys.stdout)
    
    dispatcher = Dispatcher()
    
    bot = Bot(token=settings.bot_token)
    
    await bot.set_my_commands(commands=BOT_COMMANDS)
    
    register_middlewares(dispatcher=dispatcher, settings=settings)
    
    dispatcher.include_router(router)
    
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
