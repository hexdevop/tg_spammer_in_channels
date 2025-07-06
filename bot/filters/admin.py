from aiogram.filters import BaseFilter

from variables import variables


class AdminFilter(BaseFilter):
    async def __call__(self, event) -> bool:
        return event.from_user.id in variables.admins
