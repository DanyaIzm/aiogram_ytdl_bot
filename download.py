import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import uuid4

from yt_dlp import YoutubeDL
from yt_dlp.utils import download_range_func
from utils import convert_str_to_seconds
from ytdlp_settings import NORMAL_QUALITY, BEST_QUALITY

class VideoURLType(str, Enum):
    LOCAL = "local"
    EXTERNAL = "external"

@dataclass
class Video:
    url: str
    type: VideoURLType


class VideoDownloader:
    def __init__(self, url: str):
        self.url = url
        self.cut_from: str | None = None
        self.cut_to: str | None = None
        self._progress = 0
    
    def set_cut(self, cut_from: str, cut_to: str) -> None:
        self.cut_from = cut_from
        self.cut_to = cut_to
    
    def get_progress(self) -> int:
        print(f"progress in get progress {self._progress}")
        return self._progress
    
    async def download_normal(self) -> Video:
        return await self._download()
    
    async def download_hq(self) -> Video:
        return await self._download(hq=True)
    
    def _progress_hook(self, data: dict[Any]) -> None:
        if data['status'] == 'downloading':
            self._progress = round(float(data['downloaded_bytes'])/float(data['total_bytes'])*100,1)
        elif data['status'] == 'finished':
            self._progress = 100

    async def _download(self, hq: bool = False) -> Video:
        filename = await asyncio.to_thread(self._download_in_background, hq)
        
        return Video(url=filename, type=VideoURLType.LOCAL)
    
    def _download_in_background(self, hq: bool) -> None:
        filename = f"{uuid4()}.mp4"
        
        if hq:
            format = BEST_QUALITY
        else:
            format = NORMAL_QUALITY
        
        ytdl_options = {
            "outtmpl": filename,
            "format": format,
            "merge_output_format": "mp4",
            "progress_hooks": [self._progress_hook]
        }
        
        if self.cut_from and self.cut_to:
            ytdl_options["download_ranges"] = download_range_func(None, [(convert_str_to_seconds(self.cut_from), convert_str_to_seconds(self.cut_to))])
        
        with YoutubeDL(ytdl_options) as ydl:
            ydl.download(self.url)
        
        return filename
        
        
