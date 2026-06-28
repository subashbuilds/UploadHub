import os
from urllib.parse import urlparse, unquote

import httpx

from utils.helpers import human_size


async def get_url_info(url: str):
    filename = None
    filesize = "Unknown"

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=20
        ) as client:

            response = await client.head(url)

            if response.status_code >= 400:
                response = await client.get(
                    url,
                    headers={"Range": "bytes=0-0"}
                )

            cd = response.headers.get("Content-Disposition")

            if cd and "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('"')

            if not filename:
                filename = os.path.basename(
                    unquote(urlparse(str(response.url)).path)
                )

            if not filename:
                filename = "Unknown File"

            length = response.headers.get("Content-Length")

            if length and length.isdigit():
                filesize = human_size(int(length))

    except Exception:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or "Unknown File"

    return filename, filesize