import asyncio
from logging import getLogger
from typing import TYPE_CHECKING, cast

from aiohttp import web
from dependency_injector.wiring import Provide, inject

from tosaquestbot import bot

if TYPE_CHECKING:
    from dependency_injector.providers import Configuration

logger = getLogger(__name__)


@inject
async def main(
    app: "web.Application" = Provide["http.app"],
    config: "Configuration" = Provide["http.config"],
) -> None:
    await bot.init()

    host = cast(str, config.get("host") or "127.0.0.1")
    port = cast(int, config["port"])

    logger.info("Starting application at %s:%s", host, port)

    server_task = asyncio.create_task(
        web._run_app(  # noqa: WPS437; intented  # type: ignore
            app,
            host=host,
            port=port,
            print=lambda *args: None,
            handle_signals=True,
        ),
        name="webserver",
    )

    try:
        await server_task
    except asyncio.CancelledError:
        logger.info("Shutting down application")
        server_task.cancel()
        await server_task
        logger.info("Application stopped")
