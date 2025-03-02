#
# Copyright (C) 2024-2025 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import Message

from config import BANNED_USERS
from strings import command, get_command
from YukkiMusic import tbot
from YukkiMusic.utils.database import get_lang, set_cmode
from YukkiMusic.utils.decorators.admins import admin_actual

from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import ChannelParticipantCreator
@tbot.on_message(flt.command("CHANNELPLAY_COMMAND", True) & flt.group & ~flt.user(BANNED_USERS))
@admin_actual
async def playmode_(language, _):
    chat = await event.get_chat()
    if len(event.message.text.split()) < 2:
        return await event.reply(
            _["cplay_1"].format(chat.title, _["CHANNELPLAY_COMMAND"])
        )
    query = event.message.text.split(None, 2)[1].lower().strip()
    if (str(query)).lower() == "disable":
        await set_cmode(event.chat_id, None)
        return await event.reply("Channel Play Disabled")
        
    elif str(query) == "linked":
        chat = (await tbot(GetFullChannelRequest(channel=chat.id))).full_chat
        if chat.linked_chat_id:
            chat_id = chat.linked_chat_id
            linked_chat = await tbot.get_entity(chat_id)
            await set_cmode(event.chat_id, chat_id)
            return await event.reply(
                _["cplay_3"].format(linked_chat.title, linked_chat.id)
            )
        else:
            return await event.reply(_["cplay_2"])
    else:
        try:
            chat = await tbot.get_entity(query)
        except Exception:
            return await event.reply(_["cplay_4"])
        if isinstance(chat, Channel):
        	if chat.megagroup
                return await event.reply(_["cplay_5"])
        else:
        	return await event.reply(_["cplay_5"])
        try:
        	creator, status = await tbot.get_chat_member(chat.id, event.sender_id)
        except Exception:
            return await event.reply(_["cplay_4"])

        if status != "OWNER":
            return await event.reply(_["cplay_6"].format(chat.title, creator.username))
        await set_cmode(event.chat_id, chat.id)
        return await event.reply(_["cplay_3"].format(chat.title, chat.id))