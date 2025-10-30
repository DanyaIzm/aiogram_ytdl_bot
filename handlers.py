import asyncio
from aiogram import F, Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile

from download import VideoDownloader, VideoURLType, Video

router = Router()


@router.message(Command("hq"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    if not command.args:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{message.text} в лучшем качестве")
    
    downloader = VideoDownloader(command.args)
    
    progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
    asyncio.create_task(periodically_send_progress(progress_message, downloader))
    
    video = await downloader.download_hq()
    
    await send_video_to_user(message, video)


@router.message(Command("cut"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args.split() if command.args else None
    
    if not args or len(args) != 3:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{args[0]} в нормальном качестве с {args[1]} по {args[2]}")
    
    downloader = VideoDownloader(args[0])
    downloader.set_cut(args[1], args[2])
    
    progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
    asyncio.create_task(periodically_send_progress(progress_message, downloader))
    
    video = await downloader.download_normal()
    
    await send_video_to_user(message, video)


@router.message(Command("hqcut"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args.split() if command.args else None
    
    if not args or len(args) != 3:
        return await message.answer("Неправильное использование комманды")
    
    await message.answer(f"Пытаюсь скачать видео f{args[0]} в лучшем качестве с {args[1]} по {args[2]}")
    
    downloader = VideoDownloader(args[0])
    downloader.set_cut(args[1], args[2])
    
    progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
    asyncio.create_task(periodically_send_progress(progress_message, downloader))
    
    video = await downloader.download_hq()
    
    await send_video_to_user(message, video)


@router.message(F.text)
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Пытаюсь скачать видео f{message.text} в нормальном качестве")
    downloader = VideoDownloader(message.text)
    
    progress_message = await message.answer(f"Прогресс: {downloader.get_progress()}%")
    asyncio.create_task(periodically_send_progress(progress_message, downloader))
    
    video = await downloader.download_normal()
    
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
    video_file = FSInputFile(video.url)
    
    await message.answer_video(video_file)
    

async def send_external_video_to_user(message: Message, video: Video) -> None:
    await message.answer(video.url)
