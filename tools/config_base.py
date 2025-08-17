import json
import yaml
import copy
from typing import Union, Dict, Any
from pathlib import Path


class ConfigBase:
    """Базовый класс для всех конфигураций"""

    def __init__(self):
        # Сохраняем исходные настройки для to_default()
        self._original_values = {}
        self._save_original_values()

    def _save_original_values(self):
        """Сохраняет исходные значения для возможности сброса"""
        for attr_name in dir(self):
            if not attr_name.startswith("_") and not callable(getattr(self, attr_name)):
                value = getattr(self, attr_name)
                if isinstance(value, ConfigBase):
                    self._original_values[attr_name] = copy.deepcopy(value.__dict__)
                else:
                    self._original_values[attr_name] = copy.deepcopy(value)

    def update(self, source: Union[Dict[str, Any], str]):
        """
        Обновляет значения конфигурации из словаря или файла

        Args:
            source: Словарь с настройками или путь к JSON/YAML файлу
        """
        if isinstance(source, str):
            # Читаем из файла
            file_path = Path(source)
            if not file_path.exists():
                raise FileNotFoundError(f"Файл {source} не найден")

            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".json"]:
                    data = json.load(f)
                elif file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(
                        f"Неподдерживаемый формат файла: {file_path.suffix}"
                    )
        else:
            data = source

        self._update_recursive(data)

    def _update_recursive(self, data: Dict[str, Any]):
        """Рекурсивно обновляет значения"""
        for key, value in data.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, ConfigBase) and isinstance(value, dict):
                    # Рекурсивно обновляем вложенный объект
                    current_value._update_recursive(value)
                else:
                    # Обновляем простое значение
                    setattr(self, key, value)
                    # Обновляем также переменную класса для глобального доступа
                    setattr(self.__class__, key, value)

    def to_default(self):
        """Возвращает все настройки к исходным значениям"""
        for attr_name, original_value in self._original_values.items():
            if hasattr(self, attr_name):
                current_attr = getattr(self, attr_name)
                if isinstance(current_attr, ConfigBase):
                    # Для вложенных объектов восстанавливаем каждое поле
                    for nested_key, nested_value in original_value.items():
                        if not nested_key.startswith("_"):
                            setattr(
                                current_attr, nested_key, copy.deepcopy(nested_value)
                            )
                            setattr(
                                current_attr.__class__,
                                nested_key,
                                copy.deepcopy(nested_value),
                            )
                else:
                    setattr(self, attr_name, copy.deepcopy(original_value))
                    setattr(self.__class__, attr_name, copy.deepcopy(original_value))

    def check(self, indent: int = 0):
        """
        Построчно выводит все значения переменных класса

        Args:
            indent: Уровень отступа для вложенных объектов
        """
        prefix = "    " * indent
        for attr_name in dir(self):
            if not attr_name.startswith("_") and not callable(getattr(self, attr_name)):
                attr_value = getattr(self, attr_name)
                if isinstance(attr_value, ConfigBase):
                    print(f"{prefix}{attr_name}:")
                    attr_value.check(indent + 1)
                else:
                    print(f"{prefix}{attr_name} = {repr(attr_value)}")
