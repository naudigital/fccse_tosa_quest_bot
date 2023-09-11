import argparse
import asyncio
import sys
from importlib.metadata import version
from logging import getLogger
from typing import NoReturn

import coloredlogs  # type: ignore

from tosaquestbot import main
from tosaquestbot.containers import Container
from tosaquestbot.settings import Settings

logger = getLogger("tosaquestbot")


async def bootstrap(argsv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Tosa Quest Bot")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Log level",
    )
    args = parser.parse_args(argsv)
    coloredlogs.install(level=args.log_level)  # type: ignore

    logger.info("Running tosaquestbot version %s", version(__package__))

    container = Container()

    settings = Settings()  # type: ignore

    container.config.from_dict(settings.model_dump(mode="json"))

    logger.info("Wiring packages")
    container.wire(packages=["tosaquestbot"])

    await main.main()

    return 0


def poetry_main() -> NoReturn:
    sys.exit(asyncio.run(bootstrap(sys.argv[1:])))


if __name__ == "__main__":
    poetry_main()
