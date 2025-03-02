import asyncio
import os
import re
from dataclasses import dataclass

from async_lru import alru_cache
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL

from config import YTDOWNLOADER, cookies
from YukkiMusic.decorators.asyncify import asyncify
from YukkiMusic.utils.database import is_on_off
from YukkiMusic.utils.formatters import time_to_seconds

from .enum import SourceType


@dataclass
class Track:
    title: str
    link: str
    thumb: str
    duration: int  # duration in seconds
    streamtype: SourceType
    video: bool  # The song is audio or video
    by: str | None = None  # None but required
    download_url: str | None = (
        None  # If provided directly used to download instead self.link
    )

    is_live: bool | None = None
    vidid: str | None = None
    file_path: str | None = None

    def __post_init__(self):
        if self.is_youtube:
            pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
            url = self.download_url if self.download_url else self.link
            p_match = re.search(pattern, url)
            self.vidid = p_match.group(1)
        else:
            self.vidid = self.streamtype.value

    async def is_exists(self):
        exists = False

        if self.file_path:
            if await is_on_off(YTDOWNLOADER):
                exists = os.path.exists(self.file_path)
            else:
                exists = len(self.file_path) > 30

        return exists

    @property
    def is_youtube(self) -> bool:
        url = self.download_url if self.download_url else self.link
        return "youtube.com" in url or "youtu.be" in url

    @property
    def is_telegram(self) -> bool:
        return self.streamtype == SourceType.TELEGRAM

    @property
    def is_m3u8(self) -> bool:
        return bool(self.is_live and self.title is None and self.duration is None)

    async def download(self, options: dict | None = None):
        url = self.download_url if self.download_url else self.link

        if await is_on_off(YTDOWNLOADER):
            ytdl_opts = {
                "format": (
                    "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])"
                    if self.video
                    else "bestaudio/best"
                ),
                "continuedl": True,
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "noplaylist": True,
                "nocheckcertificate": True,
                "quiet": True,
                "retries": 3,
                "no_warnings": True,
            }

            if self.is_youtube:
                ytdl_opts["cookiefile"] = cookies()

            if options:
                if isinstance(options, dict):
                    ytdl_opts.update(options)
                else:
                    raise Exception(
                        f"Expected 'options' to be a dict but got {type(options).__name__}"
                    )

            @asyncify
            def _download():
                with YoutubeDL(ytdl_opts) as ydl:
                    info = ydl.extract_info(url, False)
                    self.file_path = os.path.join(
                        "downloads", f"{info['id']}.{info['ext']}"
                    )

                    if not os.path.exists(self.file_path):
                        ydl.download([url])

                    return self.file_path

            return await _download()

        else:
            format_code = "b" if self.video else "bestaudio/best"  # Keep "b" not "best"
            command = f'yt-dlp -g -f "{format_code}" {"--cookies " + cookies() if self.is_youtube else ""} "{url}"'
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if stdout:
                self.file_path = stdout.decode().strip()
                return self.file_path
            else:
                raise Exception(f"Failed to get file path: {stderr.decode().strip()}")

    async def __call__(self, audio: bool = True):
        return self.file_path or await self.download(audio)


@alru_cache(maxsize=None)
async def search(query):
    try:
        results = VideosSearch(query, limit=1)
        for result in (await results.next())["result"]:
            return {
                "title": result["title"],
                "link": result["link"],
                "download_url": result["link"],
                "duration": (
                    time_to_seconds(result["duration"]) if result["duration"] else 0
                ),
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }
    except Exception:
        return await search_from_ytdlp(query)


@alru_cache(maxsize=None)
@asyncify
def search_from_ytdlp(query):
    options = {
        "format": "best",
        "noplaylist": True,
        "quiet": True,
        "extract_flat": "in_playlist",
        "cookiefile": cookies(),
    }

    with YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(f"ytsearch: {query}", download=False)
        details = info_dict.get("entries", [None])[0]
        if not details:
            raise ValueError("No results found.")

        return Track(
            title=details["title"],
            link=(
                details["webpage_url"].split("&")[0]
                if "&" in details["webpage_url"]
                else details["webpage_url"]
            ),
            download_url=details["webpage_url"],
            duration=details["duration"],
            thumb=details["thumbnails"][0]["url"],
        )
