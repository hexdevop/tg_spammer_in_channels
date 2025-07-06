from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_admin():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Мои каналы 🔊")
    return builder.adjust(1).as_markup(
        resize_keyboard=True, input_field_placeholder="Админ панель 🏚"
    )

