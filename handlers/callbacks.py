import os

from pyrogram import Client
from pyrogram.types import CallbackQuery

from tasks import tasks
from downloaders.telegram import download_telegram_file
from downloaders.direct import download_direct_file
from uploaders.pixeldrain import upload_to_pixeldrain


@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    destination, task_id = callback.data.split("|")

    task = tasks.get(task_id)

    if not task:
        await callback.answer("Task expired!", show_alert=True)
        return

    await callback.answer()

    message = task["message"]

    await callback.message.edit_text(
        f"⏳ Preparing upload to **{destination.title()}**..."
    )

    # Download
    if (
        message.document
        or message.video
        or message.audio
        or message.photo
        or message.animation
        or message.voice
    ):
        file_path = await download_telegram_file(
            message,
            callback.message
        )
    else:
        file_path = await download_direct_file(
            message.text,
            callback.message
        )

    try:
        await callback.message.edit_text(
            "⬆️ Uploading to PixelDrain..."
        )

        url = await upload_to_pixeldrain(file_path)

        await callback.message.edit_text(
            f"✅ Upload Complete!\n\n🔗 {url}"
        )

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Upload failed\n\n`{e}`"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)