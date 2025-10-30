from aiogram.types import BotCommand


BOT_COMMANDS = [
    BotCommand(command="hq", description="Скачать в лучшем качестве"),
    BotCommand(command="cut", description="Скачать в нормальнм качестве и обрезать. Пример: /cut youtube.com/video 1:25  5:33"),
    BotCommand(command="hqcut", description="Скачать в лучшем качестве и обрезать. Пример: /hqcut youtube.com/video 1:25  5:33"),
]