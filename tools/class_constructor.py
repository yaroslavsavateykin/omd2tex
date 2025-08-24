import json
import yaml
import copy
import sys
from typing import Union, Dict, Any
from pathlib import Path

from config_base import ConfigBase


class ClassConstructor:
    """Единый инструмент для создания и управления классами конфигурации"""

    def __init__(self, class_name: str = "Config"):
        """
        Инициализация конструктора

        Args:
            class_name: Базовое имя для создаваемого класса
        """
        self.class_name = class_name
        self.config_instance = None
        self._source_data = None

    def from_file(self, file_path: str) -> ConfigBase:
        """
        Создает класс конфигурации из JSON или YAML файла

        Args:
            file_path: Путь к файлу с настройками

        Returns:
            Экземпляр созданного класса конфигурации
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")

        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix.lower() in [".json"]:
                data = json.load(f)
            elif file_path.suffix.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_path.suffix}")

        self._source_data = data
        self.config_instance = self._create_config_from_dict(data, self.class_name)
        return self.config_instance

    def from_dict(self, data: Dict[str, Any]) -> ConfigBase:
        """
        Создает класс конфигурации из словаря

        Args:
            data: Словарь с настройками

        Returns:
            Экземпляр созданного класса конфигурации
        """
        self._source_data = data
        self.config_instance = self._create_config_from_dict(data, self.class_name)
        return self.config_instance

    def _create_config_from_dict(
        self, data: Dict[str, Any], class_name: str
    ) -> ConfigBase:
        """
        Внутренний метод для создания класса конфигурации из словаря

        Args:
            data: Словарь с настройками
            class_name: Имя создаваемого класса

        Returns:
            Экземпляр созданного класса конфигурации
        """
        # Создаем атрибуты класса
        class_attrs = {}

        # Добавляем вложенные классы как вложенные классы
        for key, value in data.items():
            if isinstance(value, dict):
                nested_class_name = key.capitalize()
                nested_config = self._create_config_from_dict(value, nested_class_name)
                class_attrs[key] = nested_config
            else:
                class_attrs[key] = value

        # Создаем новый класс динамически
        ConfigClass = type(class_name, (ConfigBase,), class_attrs)

        # Создаем экземпляр
        config_instance = ConfigClass()

        return config_instance

    def to_py_file(self, file_path: str):
        """
        Записывает созданный класс конфигурации в Python файл

        Args:
            file_path: Путь для сохранения .py файла
        """
        if self.config_instance is None:
            raise ValueError(
                "Сначала создайте конфигурацию с помощью from_file() или from_dict()"
            )

        if self._source_data is None:
            raise ValueError("Отсутствуют исходные данные для генерации файла")

        # Генерируем код класса
        py_code = self._generate_python_code(self._source_data, self.class_name)

        # Записываем в файл
        file_path = Path(file_path)
        if not file_path.suffix:
            file_path = file_path.with_suffix(".py")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(py_code)

        print(f"Класс конфигурации сохранен в файл: {file_path}")

    def _generate_python_code(
        self, data: Dict[str, Any], class_name: str, indent_level: int = 0
    ) -> str:
        """
        Генерирует код Python для класса конфигурации

        Args:
            data: Словарь с данными
            class_name: Имя класса
            indent_level: Уровень отступа для вложенных классов

        Returns:
            Строка с кодом Python
        """
        indent = "    " * indent_level
        code = ""

        # Если это корневой класс, добавляем импорты
        if indent_level == 0:
            code = "from .config_base import ConfigBase\n\n"

        # Начинаем определение класса
        code += f"{indent}class {class_name}(ConfigBase):\n"

        # Генерируем вложенные классы как вложенные в текущий класс
        for key, value in data.items():
            if isinstance(value, dict):
                nested_class_name = key.capitalize()
                nested_code = self._generate_python_code(
                    value, nested_class_name, indent_level + 1
                )
                code += nested_code + "\n"

        # Добавляем атрибуты текущего уровня (простые значения)
        for key, value in data.items():
            if not isinstance(value, dict):
                code += f"{indent}    {key} = {repr(value)}\n"

        # Добавляем разделитель перед методами
        if any(not isinstance(v, dict) for v in data.values()):
            code += "\n"

        # Добавляем __init__ метод
        code += f"{indent}    def __init__(self):\n"
        for key, value in data.items():
            if isinstance(value, dict):
                # Для вложенных классов создаем экземпляр
                code += f"{indent}        self.{key} = self.__class__.{key.capitalize()}()\n"
            else:
                code += f"{indent}        self.{key} = self.__class__.{key}\n"
        code += f"{indent}        super().__init__()\n\n"

        return code


# Пример использования:
if __name__ == "__main__":
    print(sys.argv[0:3])
    settings, classname, output = sys.argv[1:4]

    constructor = ClassConstructor(class_name=classname)

    config = constructor.from_file(settings)

    print("=== Исходная конфигурация ===")
    config.check()

    constructor.to_py_file(output)
