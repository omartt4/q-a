"""Worker entrypoint reserved for asynchronous generation jobs."""

import asyncio


async def run_worker() -> None:
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run_worker())
