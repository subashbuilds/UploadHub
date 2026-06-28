import os
from uploaders.gofile import upload_to_gofile
from pyrogram import Client
from pyrogram.types import CallbackQuery

from core.tasks import (
    get_task,
    cancel_task,
    remove_task,
)

from core.tasks import tasks
from downloaders.telegram import download_telegram_file
from downloaders.direct import download_direct_file
from uploaders.pixeldrain import upload_to_pixeldrain


@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    action, task_id = callback.data.split("|")
    
    if action == "cancel":

        cancel_task(task_id)

        await callback.message.edit_text(
            "❌ Cancelled."
        )

        remove_task(task_id)

        return

    destination = action


    task = get_task(task_id)

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
            callback.message,
            task_id
        )

    try:
        if destination == "pixeldrain":
            await callback.message.edit_text(
            "⬆️ Uploading to PixelDrain..."
        )
            url = await upload_to_pixeldrain(file_path)

        elif destination == "gofile":
            await callback.message.edit_text(
                "⬆️ Uploading to GoFile..."
        )
            url = await upload_to_gofile(file_path)

        else:
            raise Exception("Unknown upload destination.")

        await callback.message.edit_text(
            f"✅ Upload Complete!\n\n🔗 {url}"
    )

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Upload failed\n\n`{e}`"
    )

    finally:

        remove_task(task_id)

        if os.path.exists(file_path):
            os.remove(file_path)