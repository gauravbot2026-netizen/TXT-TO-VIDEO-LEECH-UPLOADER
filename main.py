# Don't Remove Credit Tg - https://t.me/roxybasicneedbot1

import os
import re
import sys
import time
import asyncio
import subprocess

import core as helper
from vars import API_ID, API_HASH, BOT_TOKEN

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ------------------ START ------------------ #
@bot.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text("👋 Send /upload and upload TXT file")

# ------------------ UPLOAD ------------------ #
@bot.on_message(filters.command("upload"))
async def upload(bot: Client, m: Message):

    msg = await m.reply_text("📤 Send TXT file")
    file: Message = await bot.listen(m.chat.id)

    path = await file.download()
    await file.delete()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    links = []
    for line in lines:
        url = re.search(r'https?://\S+', line)
        if url:
            links.append(url.group())

    os.remove(path)

    if not links:
        return await msg.edit("❌ No links found")

    await msg.edit(f"✅ Found {len(links)} links\nSend start number (1 default)")
    start_msg = await bot.listen(m.chat.id)

    try:
        count = int(start_msg.text)
    except:
        count = 1

    await start_msg.delete()

    success = 0
    failed = 0

    for i in range(count - 1, len(links)):

        url = links[i]
        name = f"{str(i+1).zfill(3)}"

        prog = await m.reply_text(f"⬇️ Downloading {i+1}/{len(links)}")

        try:
            # ----------- CMD FIX ----------- #
            if "youtu" in url:
                cmd = f'yt-dlp -f "best" "{url}" -o "{name}.%(ext)s"'

            elif url.endswith(".pdf"):
                cmd = f'yt-dlp "{url}" -o "{name}.pdf"'

            elif ".m3u8" in url:
                cmd = f'yt-dlp -f "best" "{url}" -o "{name}.mp4"'

            else:
                cmd = f'yt-dlp "{url}" -o "{name}.%(ext)s"'

            # RUN
            os.system(cmd)

            # ----------- FILE DETECT ----------- #
            file_path = None
            for ext in [".mp4", ".mkv", ".webm", ".pdf"]:
                if os.path.exists(name + ext):
                    file_path = name + ext
                    break

            if file_path:
                if file_path.endswith(".pdf"):
                    await bot.send_document(m.chat.id, file_path)
                else:
                    await bot.send_video(m.chat.id, file_path)

                os.remove(file_path)
                success += 1
            else:
                failed += 1
                await prog.edit("❌ Download failed")

        except FloodWait as e:
            await asyncio.sleep(e.value)

        except Exception as e:
            failed += 1
            await prog.edit(f"❌ Error: {str(e)}")

        await prog.delete()
        await asyncio.sleep(1)

    await m.reply_text(
        f"🎉 Done\n\n✅ Success: {success}\n❌ Failed: {failed}"
    )

# ------------------ RUN ------------------ #
bot.run()
