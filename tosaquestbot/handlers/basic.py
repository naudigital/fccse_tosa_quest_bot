from typing import TYPE_CHECKING, cast

import cv2
import numpy as np
from aiogram import F as _F  # noqa: WPS347, WPS111
from aiogram import Router, types
from aiogram.filters import Command
from dependency_injector.wiring import Provide, inject

from tosaquestbot.errors import TokenAlreadyActivatedError
from tosaquestbot.qrutils import detect_and_decode

if TYPE_CHECKING:
    from tosaquestbot.services.token import TokenService
    from tosaquestbot.services.user import UserService

router = Router()


@router.message(Command("start"))
@inject
async def start(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
) -> None:
    if not message.from_user:
        return

    if message.chat.type != "private":
        await message.answer("Бот доступний тільки в приватних повідомленнях")
        return

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    if not user:
        user = await user_service.add_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username,
        )

    await message.answer(
        f"<b>Привіт, {message.from_user.first_name}!</b>\n"
        "Фотографуй наліпки та надсилай їх сюди, щоб отримати бали за квест. "
        "Слідкуй за тим, щоб на фотографії було чітко видно QR-код поруч з наліпкою.",
    )


@router.message(Command("activate"))
@inject
async def activate(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
    user_service: "UserService" = Provide["services.user"],
) -> None:
    if not message.from_user:
        return

    if not message.text:
        return

    if message.chat.type != "private":
        await message.answer("Бот доступний тільки в приватних повідомленнях")
        return

    token_id = message.text.split(" ", 1)[1]

    token = await token_service.get_token(token_id)

    if not token:
        await message.answer("<b>Помилка:</b> Недійсний токен")
        return

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    if not user:
        user = await user_service.add_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username,
        )

    try:
        await token_service.activate_token(token, user)
    except TokenAlreadyActivatedError:
        await message.answer("<b>Помилка:</b> Ви вже активували цей токен")
        return

    activations = await token_service.get_activations_by_user(user)

    await message.answer(
        "<b>Токен активовано!</b>\n"
        f"Активовано токенів: <code>{len(activations)}</code>",
    )


@router.message(_F.photo)
@inject
async def photo(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not (message.from_user and message.photo and (message.chat.type == "private")):
        return

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    if not user:
        user = await user_service.add_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username,
        )

    photo_size = message.photo[-1]

    if not message.bot:
        return

    photo_file_path = (await message.bot.get_file(photo_size.file_id)).file_path
    if not photo_file_path:
        await message.answer("Помилка завантаження фото. Спробуйте ще раз")
        return

    photo_file = await message.bot.download_file(photo_file_path)
    if not photo_file:
        await message.answer("Помилка завантаження фото. Спробуйте ще раз")
        return

    file_bytes = np.asarray(bytearray(photo_file.read()), dtype=np.uint8)
    img = cv2.cvtColor(cv2.imdecode(file_bytes, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    decoded_text = await detect_and_decode(img)

    if not decoded_text:
        await message.answer("Не вдалося розпізнати QR-код. Спробуйте ще раз")
        return

    token_id = cast(str, decoded_text[0])
    if not token_id:
        await message.answer("Не вдалося розпізнати QR-код. Спробуйте ще раз")
        return

    token = await token_service.get_token(token_id)

    if not token:
        await message.answer("<b>Помилка:</b> Недійсний токен")
        return

    if not cast(int, token.valid):
        await message.answer("<b>Помилка:</b> Токен деактивовано")
        return

    try:
        await token_service.activate_token(token, user)
    except TokenAlreadyActivatedError:
        await message.answer("<b>Помилка:</b> Ви вже активували цей токен")
        return

    activations = await token_service.get_activations_by_user(user)

    await message.answer(
        "<b>Токен активовано!</b>\n"
        f"Активовано токенів: <code>{len(activations)}</code>",
    )
