import json
import yaml
import copy
from typing import Union, Dict, Any
from pathlib import Path


class ConfigBase:
    """Базовый класс для всех конфигураций"""

    # Хранилище оригинальных значений на уровне класса
    _class_original_values = None

    def __init__(self):
        # Сохраняем исходные настройки для to_default()
        self._save_original_values()
        self._init_instance_values()

    def _init_instance_values(self):
        """Инициализирует значения экземпляра на основе классовых атрибутов"""
        for attr_name in dir(self.__class__):
            if not attr_name.startswith("_") and not callable(
                getattr(self.__class__, attr_name)
            ):
                class_value = getattr(self.__class__, attr_name)
                if isinstance(class_value, type) and issubclass(
                    class_value, ConfigBase
                ):
                    # Для вложенных классов создаем экземпляр
                    setattr(self, attr_name, class_value())
                else:
                    setattr(self, attr_name, class_value)

    @classmethod
    def _save_class_original_values(cls):
        """Сохраняет исходные значения классовых атрибутов"""
        if cls._class_original_values is None:
            cls._class_original_values = {}
            for attr_name in dir(cls):
                if not attr_name.startswith("_") and not callable(
                    getattr(cls, attr_name)
                ):
                    value = getattr(cls, attr_name)
                    if isinstance(value, type) and issubclass(value, ConfigBase):
                        # Для вложенных классов сохраняем их оригинальные значения
                        if (
                            hasattr(value, "_class_original_values")
                            and value._class_original_values is not None
                        ):
                            cls._class_original_values[attr_name] = (
                                value._class_original_values
                            )
                        else:
                            # Если оригинальные значения еще не сохранены, сохраняем их
                            value._save_class_original_values()
                            cls._class_original_values[attr_name] = (
                                value._class_original_values
                            )
                    else:
                        cls._class_original_values[attr_name] = copy.deepcopy(value)

    @classmethod
    def update(cls, source: Union[Dict[str, Any], str]):
        """
        Обновляет значения конфигурации из словаря или файла

        Может вызываться как на уровне класса, так и на уровне экземпляра

        Args:
            source: Словарь с настройками или путь к JSON/YAML файлу
        """
        # Сохраняем оригинальные значения класса при первом вызове
        if cls._class_original_values is None:
            cls._save_class_original_values()

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

        # Определяем, вызван метод на классе или экземпляре
        if type(cls) is type and issubclass(cls, ConfigBase):
            # Вызван как classmethod - обновляем классовые атрибуты
            cls._update_class_recursive(cls, data)
        else:
            # Вызван как метод экземпляра
            self = cls
            self._update_instance_recursive(self, data)

    @classmethod
    def _update_class_recursive(cls, target, data: Dict[str, Any]):
        """Рекурсивно обновляет классовые атрибуты"""
        for key, value in data.items():
            if hasattr(target, key):
                current_value = getattr(target, key)
                if (
                    isinstance(current_value, type)
                    and issubclass(current_value, ConfigBase)
                    and isinstance(value, dict)
                ):
                    # Обновляем вложенный класс
                    cls._update_class_recursive(current_value, value)
                else:
                    # Обновляем простое значение
                    setattr(target, key, value)

    def _update_instance_recursive(self, target, data: Dict[str, Any]):
        """Рекурсивно обновляет атрибуты экземпляра"""
        for key, value in data.items():
            if hasattr(target, key):
                current_value = getattr(target, key)
                if isinstance(current_value, ConfigBase) and isinstance(value, dict):
                    # Рекурсивно обновляем вложенный объект
                    current_value._update_instance_recursive(current_value, value)
                else:
                    # Обновляем простое значение
                    setattr(target, key, value)

    @classmethod
    def to_default(cls):
        """Возвращает все настройки к исходным значениям"""
        # Определяем, вызван метод на классе или экземпляре
        if type(cls) is type and issubclass(cls, ConfigBase):
            # Вызван как classmethod - сбрасываем классовые атрибуты
            if cls._class_original_values is None:
                cls._save_class_original_values()
            cls._reset_class_to_default(cls)
        else:
            # Вызван как метод экземпляра
            self = cls
            self._reset_instance_to_default()

    @classmethod
    def _reset_class_to_default(cls, target):
        """Сбрасывает классовые атрибуты к исходным значениям"""
        if target._class_original_values is None:
            target._save_class_original_values()

        for attr_name, original_value in target._class_original_values.items():
            if hasattr(target, attr_name):
                current_attr = getattr(target, attr_name)
                if isinstance(current_attr, type) and issubclass(
                    current_attr, ConfigBase
                ):
                    # Для вложенных классов
                    target._reset_class_to_default(current_attr)
                else:
                    setattr(target, attr_name, copy.deepcopy(original_value))

    def _reset_instance_to_default(self):
        """Сбрасывает атрибуты экземпляра к исходным значениям"""
        for attr_name, original_value in self._original_values.items():
            if hasattr(self, attr_name):
                current_attr = getattr(self, attr_name)
                if isinstance(current_attr, ConfigBase):
                    # Для вложенных объектов
                    if isinstance(original_value, dict):
                        for nested_key, nested_value in original_value.items():
                            if not nested_key.startswith("_"):
                                setattr(
                                    current_attr,
                                    nested_key,
                                    copy.deepcopy(nested_value),
                                )
                else:
                    setattr(self, attr_name, copy.deepcopy(original_value))

    @classmethod
    def check(cls, indent: int = 0):
        """
        Построчно выводит все значения переменных

        Может вызываться как на уровне класса, так и на уровне экземпляра

        Args:
            indent: Уровень отступа для вложенных объектов
        """
        prefix = "    " * indent

        # Определяем, вызван метод на классе или экземпляре
        if type(cls) is type and issubclass(cls, ConfigBase):
            # Вызван как classmethod
            target = cls
            is_class = True
        else:
            # Вызван как метод экземпляра
            target = cls
            is_class = False

        # Флаг, показывающий, есть ли что-то для вывода
        has_output = False

        for attr_name in dir(target):
            if not attr_name.startswith("_") and not callable(
                getattr(target, attr_name)
            ):
                attr_value = getattr(target, attr_name)
                has_output = True

                if is_class:
                    # Для класса
                    if isinstance(attr_value, type) and issubclass(
                        attr_value, ConfigBase
                    ):
                        print(f"{prefix}{attr_name}:")
                        attr_value.check(indent + 1)
                    else:
                        print(f"{prefix}{attr_name} = {repr(attr_value)}")
                else:
                    # Для экземпляра
                    if isinstance(attr_value, ConfigBase):
                        print(f"{prefix}{attr_name}:")
                        attr_value.check(indent + 1)
                    else:
                        print(f"{prefix}{attr_name} = {repr(attr_value)}")

        # Если нет атрибутов для вывода, выводим сообщение
        if not has_output:
            print(f"{prefix}No configuration attributes found")

    def _save_original_values(self):
        """Сохраняет исходные значения для возможности сброса"""
        self._original_values = {}
        for attr_name in dir(self):
            if not attr_name.startswith("_") and not callable(getattr(self, attr_name)):
                value = getattr(self, attr_name)
                if isinstance(value, ConfigBase):
                    # Для вложенных объектов сохраняем их словарь
                    self._original_values[attr_name] = copy.deepcopy(value.__dict__)
                else:
                    self._original_values[attr_name] = copy.deepcopy(value)
