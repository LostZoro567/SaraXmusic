#
# Copyright (C) 2024-2025 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
from ..core.enum import SongType, SourceType
from .Apple import Apple
from .Carbon import Carbon
from .JioSavan import Saavn
from .Resso import Resso
from .Soundcloud import SoundCloud
from .Spotify import Spotify
from .Telegram import Telegram
from .Youtube import YouTube


class PlatForms:
    def __init__(self):
        self.apple = Apple()
        self.carbon = Carbon()
        self.saavn = Saavn()
        self.resso = Resso()
        self.soundcloud = SoundCloud()
        self.spotify = Spotify()
        self.telegram = Telegram()
        self.youtube = YouTube()

    async def valid(url: str) -> SourceType:
        services = [
            (self.apple, SourceType.APPLE),
            (self.saavn, SourceType.SAAVN),
            (self.resso, SourceType.RESSO),
            (self.soundcloud, SourceType.SOUNDCLOUD),
            (self.spotify, SourceType.SPOTIFY),
            (self.youtube, SourceType.YOUTUBE),
        ]

        for service, source_type in services:
            if await service.valid(url):
                return source_type

    async def info(
        type: SourceType, **kwargs
    ) -> (
        dict
    ):  # todo implement all classes and there info function in this function using SourceType and **kwargs
        pass

    async def download(
        type: SourceType, **kwargs
    ) -> dict:  # todo implement all downlod methdos in this download
        pass
