from typing import Optional

import logging
import asyncio
import aiohttp
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_url(
    session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore
) -> Optional[dict[str, str]]:
    timeout = aiohttp.ClientTimeout(total=15)
    async with sem:
        try:
            async with session.get(url=url, timeout=timeout) as response:
                logger.info(f"Trying to fetch with URL {url}")
                if response.status != 200:
                    logger.warning(
                        f"Unexpected status code, expected 200, but got {response.status} instead"
                    )
                    return {"url": url, "status code": response.status}

                text = await response.text()
                if text:
                    try:
                        data = json.loads(text)
                        return {"url": url, "content": data}
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from URL {url}")
                        return {"url": url, "error": "Invalid JSON"}
                else:
                    logger.warning(f"Empty response body from URL {url}")
                    return {"url": url, "error": "Empty response"}

        except (aiohttp.ClientError, asyncio.TimeoutError) as exp:
            logger.warning(f"Error fetching URL {url}, {str(exp)}")
            return {"url": url, "Error": str(exp)}


async def fetch_urls(input_file_name: str, output_file_name: str) -> None:
    with open(input_file_name, "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]
        logger.info(f"Loaded {len(urls)} URLs from file")

    async with aiohttp.ClientSession() as session:
        with open(output_file_name, "w", encoding="utf-8") as output_file:
            sem = asyncio.Semaphore(5)
            tasks = [fetch_url(session, url, sem) for url in urls]

            for future in asyncio.as_completed(tasks):
                result = await future
                if result:
                    output_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    output_file.flush()


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls_list.txt", "responses.txt"))
