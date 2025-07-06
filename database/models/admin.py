from typing import Any

from fluent.runtime import FluentLocalization
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, intpk, bigint, created_at, updated_at

from variables import Status, MediaType


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[intpk]

    chat_id: Mapped[bigint]
    title: Mapped[str]
    username: Mapped[str | None]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    @property
    def mention(self):
        if self.username:
            return f'<a href="t.me/{self.username}">{self.title}</>'
        return self.title

    def settings(self, l10n: FluentLocalization):
        return l10n.format_value(
            "channel-settings",
            {
                "chat_id": str(self.chat_id),
                "mention": self.mention,
                "username": self.username or l10n.format_value("null"),
                "created_at": self.created_at,
            },
        )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[intpk]

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))

    media_type: Mapped[MediaType]
    media: Mapped[str | None]
    text: Mapped[str] = mapped_column(Text)
    reply_markup: Mapped[dict[str, Any]]

    interval: Mapped[int]
    sent: Mapped[int] = mapped_column(default=0)
    limit: Mapped[int | None] = mapped_column(default=0)
    status: Mapped[Status] = mapped_column(default=Status.STOPPED)

    last_message_id: Mapped[int | None]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
