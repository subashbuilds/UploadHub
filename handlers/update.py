print("✅ update.py loaded")
import asyncio
import os
import sys

from pyrogram import Client, filters
from pyrogram.types import Message

from config import SUDO_USERS


@Client.on_message(filters.command("update"))
async def update_handler(client: Client, message: Message):
    
    
    print("Update command received:", message.text)
    print("User ID:", message.from_user.id)
    print("SUDO_USERS:", SUDO_USERS)
    
    
    if message.from_user.id not in SUDO_USERS:
        return

    msg = await message.reply_text("🔄 Checking for updates...")

    try:
        # Git Pull
        process = await asyncio.create_subprocess_exec(
            "git",
            "pull",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await msg.edit_text(
                f"❌ Git Pull Failed\n\n<code>{stderr.decode()}</code>"
            )
            return

        git_output = stdout.decode().strip()

        await msg.edit_text(
            f"✅ Git Updated\n\n<code>{git_output}</code>\n\n"
            "📦 Installing dependencies..."
        )

        # Install Requirements
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await msg.edit_text(
                f"❌ Dependency Installation Failed\n\n"
                f"<code>{stderr.decode()}</code>"
            )
            return

        await msg.edit_text(
            "♻️ Restarting bot..."
        )

        # Restart
        os.execvp(
            sys.executable,
            [
                sys.executable,
                "-m",
                "bot"
            ]
        )

    except Exception as e:
        await msg.edit_text(
            f"❌ <code>{e}</code>"
        )