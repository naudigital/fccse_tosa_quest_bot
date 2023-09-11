import shlex
from typing import TYPE_CHECKING

from aiogram import Router, types
from aiogram.filters import Command
from dependency_injector.wiring import Provide, inject

from tosaquestbot.adminutils import check_admin
from tosaquestbot.errors import TokenAlreadyExistsError

if TYPE_CHECKING:
    from tosaquestbot.services.token import TokenService

router = Router()


@router.message(Command("newtoken"))
@inject
async def newtoken(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    name = message.text.split(" ", 1)[1]

    try:
        token = await token_service.create_token(name)
    except TokenAlreadyExistsError:
        await message.answer("<b>Error:</b> Token already exists")
        return

    await message.answer(f"Created token <code>{token.id}</code>")


@router.message(Command("deltoken"))
@inject
async def deltoken(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    token_id = message.text.split(" ", 1)[1]

    await token_service.delete_token(token_id)

    await message.answer(f"Deleted token <code>{token_id}</code>")


@router.message(Command("checktoken"))
@inject
async def checktoken(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = shlex.split(message.text)[1:]

    if len(args) != 2:
        await message.answer("<b>Error:</b> Invalid arguments")
        return

    match args:
        case ["name", token_name]:
            token = await token_service.get_token_by_name(token_name)
        case ["id", token_id]:
            token = await token_service.get_token(token_id)
        case _:
            await message.answer("<b>Error:</b> Invalid arguments")
            return

    if not token:
        await message.answer("<b>Error:</b> Token not found")
        return

    await message.answer(
        f"id: <code>{token.id}</code>\n"
        f"name: <code>{token.name}</code>\n"
        f"valid: <code>{token.valid}</code>",
    )


@router.message(Command("modtoken"))
@inject
async def modtoken(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    args = message.text.split(" ")[1:]

    if len(args) != 2:
        await message.answer("<b>Error:</b> Invalid arguments")
        return

    token_id = args[0]
    action = args[1]

    token = await token_service.get_token(token_id)

    if not token:
        await message.answer("<b>Error:</b> Token not found")
        return

    if action == "activate":
        token.valid = True  # type: ignore
    elif action == "deactivate":
        token.valid = False  # type: ignore

    await token_service.update_token(token)

    await message.answer(
        f"id: <code>{token.id}</code>\n"
        f"name: <code>{token.name}</code>\n"
        f"valid: <code>{token.valid}</code>",
    )


@router.message(Command("listtokens"))
@inject
async def listtokens(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    tokens = await token_service.get_all_tokens()

    await message.answer(
        "\n\n".join(
            [
                f"id: <code>{token.id}</code>\n"
                f"name: <code>{token.name}</code>\n"
                f"valid: <code>{token.valid}</code>"
                for token in tokens
            ],
        ),
    )


@router.message(Command("checkactivation"))
@inject
async def checkactivation(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    activation_id = message.text.split(" ", 1)[1]

    activation = await token_service.get_activation(activation_id)

    if not activation:
        await message.answer("<b>Error:</b> Activation not found")
        return

    await message.answer(
        f"id: <code>{activation.id}</code>\n"
        f"token_id: <code>{activation.token_id}</code>\n"
        f"user_id: <code>{activation.user_id}</code>\n",
    )


@router.message(Command("revokeactivation"))
@inject
async def revokeactivation(
    message: types.Message,
    token_service: "TokenService" = Provide["services.token"],
) -> None:
    if not message.from_user:
        return

    if not check_admin(message.from_user.id):
        return

    if not message.text:
        return

    activation_id = message.text.split(" ", 1)[1]

    activation = await token_service.get_activation(activation_id)

    if not activation:
        await message.answer("<b>Error:</b> Activation not found")
        return

    await token_service.revoke_activation(activation)

    await message.answer(
        f"Revoked activation <code>{activation_id}</code>",
    )
