import asyncio
import logging
import traceback
from aiogram import F, Bot, Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandObject
from aiogram.types import ErrorEvent, Message, FSInputFile
from aiohttp import ClientOSError
import yt_dlp

from download import VideoDownloader, VideoURLType, Video

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("hq"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    if not command.args:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{message.text} в лучшем качестве")
    
    with VideoDownloader(command.args) as downloader:
        progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
        progress_task = asyncio.create_task(periodically_send_progress(progress_message, downloader))
        
        try:
            video = await downloader.download_hq()
        except yt_dlp.utils.DownloadError:
            await message.answer("Неправильная ссылка")
            return
        finally: 
            progress_task.cancel()
    
        await send_video_to_user(message, video)


@router.message(Command("cut"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args.split() if command.args else None
    
    if not args or len(args) != 3:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{args[0]} в нормальном качестве с {args[1]} по {args[2]}")
    
    with VideoDownloader(args[0]) as downloader:
        downloader.set_cut(args[1], args[2])
        
        progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
        progress_task = asyncio.create_task(periodically_send_progress(progress_message, downloader))
        
        try:
            video = await downloader.download_normal()
        except yt_dlp.utils.DownloadError:
            await message.answer("Неправильная ссылка")
            return
        finally: 
            progress_task.cancel()
    
        await send_video_to_user(message, video)


@router.message(Command("hqcut"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args.split() if command.args else None
    
    if not args or len(args) != 3:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{args[0]} в лучшем качестве с {args[1]} по {args[2]}")
    
    with VideoDownloader(args[0]) as downloader:
        downloader.set_cut(args[1], args[2])
        
        progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
        progress_task = asyncio.create_task(periodically_send_progress(progress_message, downloader))
        
        try:
            video = await downloader.download_hq()
        except yt_dlp.utils.DownloadError:
            await message.answer("Неправильная ссылка")
            return
        finally: 
            progress_task.cancel()
    
        await send_video_to_user(message, video)


@router.message(F.text)
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Пытаюсь скачать видео f{message.text} в нормальном качестве")
    
    with VideoDownloader(message.text) as downloader:
        progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
        progress_task = asyncio.create_task(periodically_send_progress(progress_message, downloader))
        
        try:
            video = await downloader.download_normal()
        except yt_dlp.utils.DownloadError:
            await message.answer("Неправильная ссылка")
            return
        finally: 
            progress_task.cancel()
    
        await send_video_to_user(message, video)


async def periodically_send_progress(message: Message, downloader: VideoDownloader) -> None:
    last_progress = downloader.get_progress()
    
    while True:
        current_progress = downloader.get_progress()
        
        if last_progress != current_progress:
            await message.edit_text(f"Прогресс: {downloader.get_progress()}%")
        
        if current_progress == 100:
            break
        
        last_progress = current_progress
        await asyncio.sleep(1)


async def send_video_to_user(message: Message, video: Video) -> None:
    match video.type:
        case VideoURLType.LOCAL:
            await send_local_video_to_user(message, video)
        case VideoURLType.EXTERNAL:
            await send_external_video_to_user(message, video)


async def send_local_video_to_user(message: Message, video: Video) -> None:
    try:
        video_file = FSInputFile(video.url)
        await message.answer_video(video_file)
    except TelegramNetworkError:
        await message.answer("Не удалось отправить видео. Возможно, оно слишком тяжелое")
        raise


async def send_external_video_to_user(message: Message, video: Video) -> None:
    await message.answer(video.url)


@router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
    await message.answer(f"Ошибка: {event.exception}")
