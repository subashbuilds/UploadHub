from pyrogram import Client
from pyrogram.types import CallbackQuery
from downloaders.direct import download_direct_file
from tasks import tasks
from downloaders.telegram import download_telegram_file


@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    data = callback.data

    destination, task_id = data.split("|")

    task = tasks.get(task_id)

    if not task:
        await callback.answer("Task expired!", show_alert=True)
        return

    await callback.answer()

    message = task["message"]

    await callback.message.edit_text(
        f"⏳ Preparing upload to **{destination.title()}**..."
    )

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

        await callback.message.edit_text(
            f"✅ Download complete!\n\n`{file_path}`"
        )
    else:
        file_path = await download_direct_file(
        message.text,
        callback.message
    )

    await callback.message.edit_text(
        f"✅ Download complete!\n\n`{file_path}`"
    )