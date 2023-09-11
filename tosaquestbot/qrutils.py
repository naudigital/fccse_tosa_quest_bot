import asyncio
import atexit
from concurrent import futures
from logging import getLogger
from typing import cast

from cv2.typing import MatLike
from qreader import QReader  # type: ignore

pool = futures.ThreadPoolExecutor()

qreader = QReader()

logger = getLogger(__name__)


async def detect_and_decode(img: MatLike) -> tuple[str | None]:
    logger.info("Detecting and decoding QR code")
    loop = asyncio.get_running_loop()
    return cast(
        tuple[str | None],  # noqa: WPS465
        await loop.run_in_executor(pool, qreader.detect_and_decode, img),  # type: ignore
    )


def free_pool() -> None:
    pool.shutdown()
    atexit.unregister(free_pool)


atexit.register(free_pool)
