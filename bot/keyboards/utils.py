from typing import Union, Tuple, List

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluent.runtime import FluentLocalization

back_text = "Назад 🔙"
cancel_text = "🚫 Отмена"


def back(data: CallbackData, l10n: FluentLocalization, value: str):
    builder = InlineKeyboardBuilder()
    data.action = value
    builder.button(text=l10n.format_value("back"), callback_data=data.pack())
    return builder.as_markup()


def cancel(data: Union[str, CallbackData], value: str = None):
    builder = InlineKeyboardBuilder()
    if type(data) is str:
        callback_data = data
    else:
        data.action = value or "cancel"
        callback_data = data.pack()
    builder.button(text=cancel_text, callback_data=callback_data)
    return builder.as_markup()


def confirm(
    data: CallbackData,
    confirm_value: str = "confirm",
    cancel_value: str = "cancel",
):
    builder = InlineKeyboardBuilder()
    data.action = confirm_value
    builder.button(text="Подтвердить ✅", callback_data=data.pack())
    data.action = cancel_value
    builder.button(text=cancel_text, callback_data=data.pack())
    return builder.adjust(1).as_markup()


def with_pagination(
    builder: InlineKeyboardBuilder,
    data: CallbackData,
    length: int,
    page: int,
    sizes: list,
    as_markup: bool = True,
    length_text: str = "{page} из {length}",
) -> Tuple[InlineKeyboardBuilder, list]:
    buttons_count = 0
    if page > 1:
        data.action = "page"
        data.page = page - 1
        builder.button(text="⏪", callback_data=data.pack())
        buttons_count += 1
    if length > 1:
        data.action = "length"
        builder.button(
            text=length_text.format(page=page, length=length), callback_data=data.pack()
        )
        buttons_count += 1
    if page < length:
        data.action = "page"
        data.page = page + 1
        builder.button(text="⏩", callback_data=data.pack())
        buttons_count += 1
    data.action = "page"
    second_row_buttons_count = 0
    if page - 9 > 1:
        data.page = page - 10
        builder.button(text="⏮ 10", callback_data=data.pack())
        second_row_buttons_count += 1
    if page + 9 < length:
        data.page = page + 10
        builder.button(text="10 ⏭", callback_data=data.pack())
        second_row_buttons_count += 1
    if buttons_count > 0:
        sizes.append(buttons_count)
    if second_row_buttons_count > 0:
        sizes.append(second_row_buttons_count)
    if as_markup:
        return builder.adjust(*sizes).as_markup()
    else:
        return builder, sizes


def generate_sizes(sizes: List, object_list: List, width: int, height: int, page: int):
    s = width * height
    for i in range(height):
        size = len(
            object_list[s * (page - 1) + i * width : s * (page - 1) + (i + 1) * width]
        )
        if size > 0:
            sizes.append(size)
    return sizes


def generate_sizes_for_cards(sizes: List, object_list: List, width: int, height: int):
    for i in range(height):
        size = len(object_list[i * width : (i + 1) * width])
        if size > 0:
            sizes.append(size)
    return sizes
