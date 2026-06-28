import re
from tasks import create_task
from utils.helpers import human_size
from utils.url_info import get_url_info

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

URL_PATTERN = re.compile(r"^https?://\S+$")


@Client.on_message(
    filters.private
    & ~filters.command("start")
)
async def message_handler(client: Client, message: Message):

    file_name = None
    file_size = None
    input_type = None

    # Telegram document
    if message.document:
        file_name = message.document.file_name
        file_size = human_size(message.document.file_size)
        input_type = "telegram"

    # Telegram video
    elif message.video:
        file_name = message.video.file_name or "video.mp4"
        file_size = human_size(message.video.file_size)
        input_type = "telegram"

    # Telegram audio
    elif message.audio:
        file_name = message.audio.file_name
        file_size = human_size(message.audio.file_size)
        input_type = "telegram"

    # Direct Link
    elif message.text and URL_PATTERN.match(message.text):
        file_name, file_size = await get_url_info(message.text)
        input_type = "url"

    else:
        return
    
    task_id = create_task(message)

    keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "📦 PixelDrain",
                callback_data=f"pixeldrain|{task_id}"
            ),
            InlineKeyboardButton(
                "☁️ GoFile",
                callback_data=f"gofile|{task_id}"
            )
        ]
    ]
    )

    await message.reply_text(
        f"📄 **File:** `{file_name}`\n"
        f"📦 **Size:** `{file_size}`\n\n"
        "Choose upload destination:",
        reply_markup=keyboard,
    )