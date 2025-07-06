from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from bot.keyboards.admin import reply


router = Router()

@router.message(CommandStart())
async def menu(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    await message.answer(
        text=l10n.format_value("admin-menu"), reply_markup=reply.main_admin()
    )
