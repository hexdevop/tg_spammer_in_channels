from pydantic import BaseModel, Field


class SomeModel(BaseModel):
    some_data: str = Field(default_factory=[])
