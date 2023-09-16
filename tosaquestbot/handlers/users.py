from typing import TYPE_CHECKING, cast

from aiogram import Router, types
from aiogram.filters import Command
from dependency_injector.wiring import Provide, inject

from tosaquestbot.adminutils import check_admin

if TYPE_CHECKING:
    from tosaquestbot.services.token import TokenService
    from tosaquestbot.services.user import UserService

router = Router()


@router.message(Command("checkuser"))
@inject
async def checkuser(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = message.text.split(" ")[1:]

    match args:
        case ["me"]:
            user = await user_service.get_user_by_telegram_id(message.from_user.id)
        case ["id", user_id]:
            user = await user_service.get_user(user_id)
        case ["tgid", tgid]:
            user = await user_service.get_user_by_telegram_id(int(tgid))
        case _:
            await message.answer("Invalid arguments")
            return

    if not user:
        await message.answer("User not found")
        return

    user_activations = await token_service.get_activations_by_user(user)

    text = (
        f"id: <code>{user.id}</code>\n"
        f"telegram_id: <code>{user.telegram_id}</code>\n"
        f"first_name: <code>{user.first_name}</code>\n"
        f"username: <code>{user.username}</code>\n"
        f"activations_count: <code>{len(user_activations)}</code>\n"
        "\n"
        "Activations:\n"
    )

    for activation in user_activations:
        token = await token_service.get_token(str(activation.token_id))
        if not token:
            continue
        text += f"- {token.name}: <code>{activation.id}</code>\n"

    text += "\n\n" f"<a href='tg://user?id={user.telegram_id}'>Open in Telegram</a>"

    await message.answer(text)


@router.message(Command("topusers"))
@inject
async def topusers(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = message.text.split(" ")[1:]

    if len(args) != 1:
        await message.answer("Invalid arguments")
        return

    count = int(args[0])

    users = await user_service.get_top_users(count)

    text = "<b>Top users:</b>\n"

    for user in users:
        user_activations = await token_service.get_activations_by_user(user)
        text += f"- <code>{user.id}</code>: " f"<b>{len(user_activations)}</b>\n"

    await message.answer(text)


@router.message(Command("alluserscsv"))
@inject
async def alluserscsv(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    users = await user_service.get_all_users()

    text = "id,telegram_id,first_name,username\n"
    for user in users:  # noqa: WPS519
        text += (
            f"{user.id},"
            f"{user.telegram_id},"
            f"{user.first_name},"
            f"{user.username}\n"
        )

    await message.answer_document(
        types.BufferedInputFile(text.encode(), filename="users.csv"),
    )


@router.message(Command("sendtext"))
@inject
async def sendtext(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = message.text.split(" ", 2)[1:]

    if len(args) != 2:
        await message.answer("Invalid arguments")
        return

    user_id = args[0]
    text = args[1]

    user = await user_service.get_user(user_id)

    if not user:
        await message.answer("User not found")
        return

    if not message.bot:
        return

    await message.bot.send_message(cast(int, user.telegram_id), text)


@router.message(Command("sendtop"))
@inject
async def sendtop(
    message: types.Message,
    user_service: "UserService" = Provide["services.user"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = message.text.split(" ", 2)[1:]

    if len(args) != 2:
        await message.answer("Invalid arguments")
        return

    count = int(args[0])
    text = args[1]

    users = await user_service.get_top_users(count)

    if not message.bot:
        return

    for user in users:
        await message.bot.send_message(cast(int, user.telegram_id), text)
