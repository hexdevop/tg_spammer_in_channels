import json
from pathlib import Path

from pydantic import BaseModel

from typing import List, Optional


class VariableModel(BaseModel):
    admins: List[int]
    throttling_default_time: int
    username: Optional[str]

    class Config:
        extra = "allow"


class Variables:
    _file_path: Path
    _data: VariableModel

    def __init__(self, file_path: str = "variables/variables.json"):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            self._file_path.write_text("")  # Инициализация пустым объектом
        self._load()

    def _load(self):
        """Загружает данные из JSON-файла в Pydantic-модель."""
        with open(self._file_path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        self._data = VariableModel(**raw_data)

    def save(self):
        """Сохраняет данные из Pydantic-модели в JSON-файл."""
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(self._data.model_dump(), file, indent=4, ensure_ascii=False)

    def __getattr__(self, item):
        """Позволяет обращаться к данным как к атрибутам."""
        if hasattr(self._data, item):
            return getattr(self._data, item)
        raise AttributeError(f"'Variables' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        """Позволяет изменять данные как атрибуты."""
        if key in {"_file_path", "_data"}:
            super().__setattr__(key, value)
        elif hasattr(self._data, key):
            setattr(self._data, key, value)
        else:
            raise AttributeError(f"'Variables' object has no attribute '{key}'")


variables = Variables()

import atexit

atexit.register(variables.save)
