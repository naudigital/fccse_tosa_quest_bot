from typing import TYPE_CHECKING, cast

from dependency_injector.wiring import Provide, inject

if TYPE_CHECKING:
    from dependency_injector.providers import Configuration


@inject
def check_admin(telegram_id: int, config: "Configuration" = Provide["config"]) -> bool:
    return telegram_id in cast(list[int], config["bot_admins"])
