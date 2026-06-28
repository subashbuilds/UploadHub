import os
from urllib.parse import urlparse, unquote

import aiofiles
import httpx

from config import DOWNLOAD_PATH
from utils.progress import progress
from core.tasks import is_cancelled


async def download_direct_file(
    url: str,
    status_message=None,
    task_id=None
):
    """
    Download a file from a direct URL with progress.
    """

    if status_message:
        await status_message.edit_text("⬇️ Starting download...")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=None
    ) as client:

        async with client.stream("GET", url) as response:

            response.raise_for_status()

            # Filename
            filename = None

            content_disposition = response.headers.get(
                "Content-Disposition"
            )

            if (
                content_disposition
                and "filename=" in content_disposition
            ):
                filename = (
                    content_disposition
                    .split("filename=")[-1]
                    .strip('"')
                )

            if not filename:
                filename = os.path.basename(
                    unquote(
                        urlparse(str(response.url)).path
                    )
                )

            if not filename:
                filename = "downloaded_file"

            file_path = os.path.join(
                DOWNLOAD_PATH,
                filename
            )

            # File Size
            length = response.headers.get("Content-Length")

            total = (
                int(length)
                if length and length.isdigit()
                else 0
            )

            current = 0

            async with aiofiles.open(file_path, "wb") as f:

                async for chunk in response.aiter_bytes(1024 * 256):

                    if task_id and is_cancelled(task_id):
                        raise Exception("❌ Download cancelled by user.")

                    await f.write(chunk)

                    current += len(chunk)

                   if status_message:
                       await progress(
            current,
            total,
            status_message,
            "⬇️ Downloading..."
        )

    return file_path