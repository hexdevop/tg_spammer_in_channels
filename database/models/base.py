import datetime
from typing import Any, Annotated

from sqlalchemy import JSON, func, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, mapped_column

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
bigint = Annotated[int, mapped_column(BigInteger, primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime.datetime, mapped_column(server_default=func.now(), onupdate=func.now())
]


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON,
        str: String(255),
    }
