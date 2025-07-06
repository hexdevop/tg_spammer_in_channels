import enum


class Status(enum.Enum):
    WORKING = "Включён 🟢"
    STOPPED = "Выключён 🔴"


class MediaType(enum.Enum):
    TEXT = "Текст 💬"
    ANIMATION = "Гиф 🖼"
    AUDIO = "Песни 🎵"
    DOCUMENT = "Документ 🗂"
    PHOTO = "Фото 🌄"
    STICKER = "Стикер 🚀"
    VIDEO = "Видео 📹"
    VIDEO_NOTE = "Кружок 📀"
    VOICE = "Голосовое 🎙"
