from aiogram import Bot, Dispatcher
from aiohttp import web
from dependency_injector import containers, providers

from tosaquestbot.db import database
from tosaquestbot.services import token, user


class HttpContext(containers.DeclarativeContainer):
    """Container for HTTP context objects."""

    config = providers.Configuration()

    app = providers.Singleton(web.Application)


class Services(containers.DeclarativeContainer):
    """Container for services."""

    db = providers.Dependency(database.Database)
    user = providers.Singleton(user.UserService, db=db)
    token = providers.Singleton(token.TokenService, db=db)


class BotContext(containers.DeclarativeContainer):
    """Container for bot context objects."""

    config = providers.Configuration()

    bot = providers.Singleton(
        Bot,
        token=config.bot_token,
    )

    dispatcher = providers.Singleton(
        Dispatcher,
        bot=bot,
    )


class Container(containers.DeclarativeContainer):
    """Application container."""

    config = providers.Configuration()

    db = providers.Singleton(
        database.Database,
        url=config.db_url,
    )
    services = providers.Container(
        Services,
        db=db,
    )
    bot_context = providers.Container(
        BotContext,
        config=config,
    )
    http = providers.Container(
        HttpContext,
        config=config.http,
    )
