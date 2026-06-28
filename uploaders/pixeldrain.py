import os
import aiohttp

from config import PIXELDRAIN_API_KEY


async def upload_to_pixeldrain(file_path: str):

    url = "https://pixeldrain.com/api/file"

    auth = aiohttp.BasicAuth(
        login="",
        password=PIXELDRAIN_API_KEY
    )

    form = aiohttp.FormData()

    form.add_field(
        "file",
        open(file_path, "rb"),
        filename=os.path.basename(file_path),
        content_type="application/octet-stream",
    )

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(url, data=form) as response:

            text = await response.text()

            if response.status != 200:
                raise Exception(
                    f"PixelDrain Error {response.status}\n{text}"
                )

            data = await response.json()

    if not data.get("success", True):
        raise Exception(data.get("message", "Upload failed"))

    return f"https://pixeldrain.com/u/{data['id']}"