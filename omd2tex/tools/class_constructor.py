import json
import yaml
import copy
import sys
from typing import Union, Dict, Any
from pathlib import Path


from omd2tex.tools.config_base import ConfigBase


class ClassConstructor:
    def __init__(self, class_name: str = "Config") -> None:
        """Initialize the dynamic class constructor with a target class name."""
        self.class_name = class_name
        self.config_instance = None
        self._source_data = None

    def from_file(self, file_path: str) -> ConfigBase:
        """Create a configuration instance from a JSON or YAML file.

        Args:
            file_path: Path to the configuration file.

        Returns:
            Instantiated ConfigBase subclass populated with file contents.

        Raises:
            FileNotFoundError: If the file is absent.
            ValueError: If the file has an unsupported extension.
            json.JSONDecodeError or yaml.YAMLError: If parsing fails.
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
        """Create a configuration instance directly from a dictionary."""
        self._source_data = data
        self.config_instance = self._create_config_from_dict(data, self.class_name)
        return self.config_instance

    def _create_config_from_dict(
        self, data: Dict[str, Any], class_name: str
    ) -> ConfigBase:
        """Recursively build ConfigBase subclasses from nested dictionaries."""
        class_attrs = {}

        for key, value in data.items():
            if isinstance(value, dict):
                nested_class_name = key.capitalize()
                nested_config = self._create_config_from_dict(value, nested_class_name)
                class_attrs[key] = nested_config
            else:
                class_attrs[key] = value

        ConfigClass = type(class_name, (ConfigBase,), class_attrs)

        config_instance = ConfigClass()

        return config_instance

    def to_py_file(self, file_path: str) -> None:
        """Serialize the generated configuration class to a Python file.

        Args:
            file_path: Destination path; ``.py`` is appended if missing.

        Returns:
            None

        Raises:
            ValueError: If configuration has not been built prior to writing.
            IOError: Propagated on file write errors.
        """
        if self.config_instance is None:
            raise ValueError(
                "Сначала создайте конфигурацию с помощью from_file() или from_dict()"
            )

        if self._source_data is None:
            raise ValueError("Отсутствуют исходные данные для генерации файла")

        py_code = self._generate_python_code(self._source_data, self.class_name)

        file_path = Path(file_path)
        if not file_path.suffix:
            file_path = file_path.with_suffix(".py")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(py_code)

        print(f"Класс конфигурации сохранен в файл: {file_path}")

    def _generate_python_code(
        self, data: Dict[str, Any], class_name: str, indent_level: int = 0
    ) -> str:
        """Generate Python source code for the dynamic configuration classes."""
        indent = "    " * indent_level
        code = ""

        if indent_level == 0:
            code = "from .config_base import ConfigBase\n\n"

        code += f"{indent}class {class_name}(ConfigBase):\n"

        for key, value in data.items():
            if isinstance(value, dict):
                nested_class_name = key.capitalize()
                nested_code = self._generate_python_code(
                    value, nested_class_name, indent_level + 1
                )
                code += nested_code + "\n"

        for key, value in data.items():
            if not isinstance(value, dict):
                code += f"{indent}    {key} = {repr(value)}\n"

        if any(not isinstance(v, dict) for v in data.values()):
            code += "\n"

        code += f"{indent}    def __init__(self):\n"
        for key, value in data.items():
            if isinstance(value, dict):
                code += f"{indent}        self.{key} = self.__class__.{key.capitalize()}()\n"
            else:
                code += f"{indent}        self.{key} = self.__class__.{key}\n"
        code += f"{indent}        super().__init__()\n\n"

        return code


if __name__ == "__main__":
    print(sys.argv[0:3])
    settings, classname, output = sys.argv[1:4]

    constructor = ClassConstructor(class_name=classname)

    config = constructor.from_file(settings)

    print("=== Исходная конфигурация ===")
    config.check()

    constructor.to_py_file(output)
