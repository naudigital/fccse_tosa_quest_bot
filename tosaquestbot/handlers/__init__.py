"""Handlers for the bot."""
from aiogram import Router

from tosaquestbot.handlers import basic, token, users

router = Router()
router.include_router(basic.router)
router.include_router(token.router)
router.include_router(users.router)
