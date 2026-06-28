import os
import aiohttp

from config import GOFILE_API_TOKEN


async def upload_to_gofile(file_path: str):

    url = "https://upload.gofile.io/uploadfile"

    headers = {
        "Authorization": f"Bearer {GOFILE_API_TOKEN}"
    }

    form = aiohttp.FormData()

    with open(file_path, "rb") as file:
        form.add_field(
            "file",
            file,
            filename=os.path.basename(file_path),
            content_type="application/octet-stream"
        )

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, data=form) as response:

                text = await response.text()
                
                print(headers)

                print("Status:", response.status)
                print("Body:", text)

                try:
                    data = await response.json(content_type=None)
                except Exception:
                    raise Exception(
                        f"HTTP {response.status}\n\n{text}"
                 )

                if response.status not in (200, 201):
                    raise Exception(
                        data.get("message", f"HTTP {response.status}")
                    )

    if data.get("status") != "ok":
        raise Exception(data.get("message", "Upload failed"))

    return data["data"]["downloadPage"]