import asyncio
import os

from pyrogram import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from core.tasks import (
    get_task,
    cancel_task,
    remove_task,
)

from downloaders.telegram import download_telegram_file
from downloaders.direct import download_direct_file

from uploaders.pixeldrain import upload_to_pixeldrain
from uploaders.gofile import upload_to_gofile


@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):

    action, task_id = callback.data.split("|")

    cancel_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data=f"cancel|{task_id}"
                )
            ]
        ]
    )

    # Cancel request
    if action == "cancel":

        cancel_task(task_id)

        await callback.answer(
            "Cancelling...",
            show_alert=False
        )

        return

    destination = action

    task = get_task(task_id)

    if not task:
        await callback.answer(
            "Task expired!",
            show_alert=True
        )
        return

    await callback.answer()

    message = task["message"]

    file_path = None

    try:

        await callback.message.edit_text(
            f"⏳ Preparing upload to **{destination.title()}**...",
            reply_markup=cancel_keyboard
        )

        # Telegram file
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
                callback.message,
                task_id,
                cancel_keyboard
            )

        # Direct URL
        else:

            file_path = await download_direct_file(
                message.text,
                callback.message,
                task_id,
                cancel_keyboard
            )

        # Upload
        if destination == "pixeldrain":

            await callback.message.edit_text(
                "⬆️ Uploading to PixelDrain...",
                reply_markup=cancel_keyboard
            )

            url = await upload_to_pixeldrain(file_path)

        elif destination == "gofile":

            await callback.message.edit_text(
                "⬆️ Uploading to GoFile...",
                reply_markup=cancel_keyboard
            )

            url = await upload_to_gofile(file_path)

        else:
            raise Exception("Unknown upload destination.")

        await callback.message.edit_text(
            f"✅ Upload Complete!\n\n🔗 {url}"
        )

    except asyncio.CancelledError:

        await callback.message.edit_text(
            "❌ Operation cancelled."
        )

    except Exception as e:

        await callback.message.edit_text(
            f"❌ Upload failed\n\n`{e}`"
        )

    finally:

        remove_task(task_id)

        if (
            file_path
            and os.path.exists(file_path)
        ):
            os.remove(file_path)
    await callback.message.edit_text(
        f"✅ Upload Complete!\n\n🔗 {url}"
    )

except asyncio.CancelledError:

    await callback.message.edit_text(
        "❌ Operation cancelled."
    )

except Exception as e:

    await callback.message.edit_text(
        f"❌ Upload failed\n\n`{e}`"
    )

finally:

    remove_task(task_id)

    if file_path and os.path.exists(file_path):
        os.remove(file_path)
