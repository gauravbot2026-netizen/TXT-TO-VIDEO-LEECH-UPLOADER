# Don't Remove Credit Tg - https://t.me/roxybasicneedbot1

import os
import re
import sys
import time
import asyncio
import subprocess

import core as helper
from vars import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB_CHANNEL

from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================== FORCE SUB ==================

async def is_subscribed(bot, user_id):
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in [
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        ]
    except UserNotParticipant:
        return False
    except:
        return False


def force_subscribe(func):
    async def wrapper(bot, message):
        if FORCE_SUB_CHANNEL:
            if not await is_subscribed(bot, message.from_user.id):
                await message.reply_text("Join channel first!")
                return
        await func(bot, message)
    return wrapper

# ================== START ==================

@bot.on_message(filters.command("start"))
@force_subscribe
async def start(bot, m):
    await m.reply_text("Send /upload to start 🚀")

# ================== UPLOAD ==================

@bot.on_message(filters.command("upload"))
@force_subscribe
async def upload(bot: Client, m: Message):

    editable = await m.reply_text("Send TXT file")

    input: Message = await bot.listen(m.chat.id)
    file_path = await input.download()
    await input.delete()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    links = []
    for line in lines:
        match = re.search(r'https?://[^\s]+', line)
        if match:
            links.append(match.group())

    os.remove(file_path)

    if not links:
        await editable.edit("No links found ❌")
        return

    await editable.edit(f"Total links: {len(links)}")

    # QUALITY
    await m.reply_text("Enter quality (144/240/360/480/720/1080)")
    q = (await bot.listen(m.chat.id)).text

    count = 1

    for url in links:
        try:
            name = f"{count:03d}"

            # ========= FIXED BLOCK =========
            if "youtu" in url:
                ytf = f"b[height<={q}]"
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.%(ext)s"'

            elif url.endswith(".pdf"):
                cmd = f'yt-dlp -o "{name}.pdf" "{url}"'

            elif ".m3u8" in url:
                cmd = f'yt-dlp "{url}" -o "{name}.mp4"'

            else:
                cmd = f'yt-dlp "{url}" -o "{name}.%(ext)s"'
            # ===============================

            msg = await m.reply_text(f"Downloading {name}...")

            subprocess.run(cmd, shell=True)

            file = None
            for ext in [".mp4", ".mkv", ".webm", ".pdf"]:
                if os.path.exists(name + ext):
                    file = name + ext
                    break

            if file:
                await m.reply_document(file)
                os.remove(file)

            await msg.delete()
            count += 1
            time.sleep(1)

        except FloodWait as e:
            await asyncio.sleep(e.value)

        except Exception as e:
            await m.reply_text(f"Error: {e}")

    await m.reply_text("Done ✅")

# ================== RUN ==================

if __name__ == "__main__":
    print("Bot Started...")
    bot.run()
