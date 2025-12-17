import copy
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Union


class ConfigBase:
    _class_original_values: Dict[str, Any] = None

    @classmethod
    def _save_class_original_values(cls) -> None:
        """Snapshot class attribute defaults for later restoration.

        Args:
            cls: Target configuration class.

        Returns:
            None

        Side Effects:
            Populates the class-level `_class_original_values` cache.
        """
        if cls._class_original_values is None:
            cls._class_original_values = {}
            for name in dir(cls):
                if name.startswith("_") or callable(getattr(cls, name)):
                    continue
                value = getattr(cls, name)
                if isinstance(value, type) and issubclass(value, ConfigBase):
                    value._save_class_original_values()
                    cls._class_original_values[name] = copy.deepcopy(
                        value._class_original_values
                    )
                else:
                    cls._class_original_values[name] = copy.deepcopy(value)

    @classmethod
    def update(cls, source: Union[Dict[str, Any], str]) -> None:
        """Update configuration values from a dict or file path.

        Args:
            source: Mapping of overrides or path to a JSON/YAML file with settings.

        Returns:
            None

        Raises:
            FileNotFoundError: If a provided file path does not exist.
            ValueError: When the file format is unsupported.
            json.JSONDecodeError or yaml.YAMLError: If configuration parsing fails.
        """
        if cls._class_original_values is None:
            cls._save_class_original_values()

        if isinstance(source, str):
            file_path = Path(source)
            if not file_path.exists():
                raise FileNotFoundError(f"Файл {source} не найден")

            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() == ".json":
                    data = json.load(f)
                elif file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Неподдерживаемый формат: {file_path.suffix}")
        else:
            data = source

        cls._update_class_recursive(cls, data)

    @classmethod
    def _update_class_recursive(cls, target, data: Dict[str, Any]) -> None:
        """Recursively propagate configuration values to nested ConfigBase subclasses.

        Args:
            target: Configuration class or subclass instance to modify.
            data: Mapping of values to apply.

        Returns:
            None
        """
        for key, value in data.items():
            attr_name = (
                key
                if hasattr(target, key)
                else key.capitalize()
                if hasattr(target, key.capitalize())
                else None
            )
            if attr_name is None:
                continue

            current_value = getattr(target, attr_name)
            if (
                isinstance(current_value, type)
                and issubclass(current_value, ConfigBase)
                and isinstance(value, dict)
            ):
                cls._update_class_recursive(current_value, value)
            else:
                setattr(target, attr_name, value)

    @classmethod
    def to_default(cls) -> None:
        """Restore configuration values to their original defaults.

        Args:
            cls: Target configuration class.

        Returns:
            None

        Side Effects:
            Mutates class attributes back to saved defaults.
        """
        if cls._class_original_values is None:
            cls._save_class_original_values()
        cls._reset_class_to_default(cls)

    @classmethod
    def _reset_class_to_default(cls, target) -> None:
        """Recursively reset configuration attributes to their saved defaults.

        Args:
            target: Configuration class or subclass to reset.

        Returns:
            None

        Side Effects:
            Mutates the target's attributes in place.
        """
        if target._class_original_values is None:
            target._save_class_original_values()

        for name, original_value in target._class_original_values.items():
            if isinstance(original_value, dict):
                # вложенный класс
                nested_class = getattr(target, name, None)
                if isinstance(nested_class, type) and issubclass(
                    nested_class, ConfigBase
                ):
                    target._reset_class_to_default(nested_class)
            else:
                setattr(target, name, copy.deepcopy(original_value))

    @classmethod
    def check(cls, indent: int = 0) -> None:
        """Print configuration values for debugging purposes.

        Args:
            indent: Current indentation level for nested configuration output.

        Returns:
            None

        Side Effects:
            Prints configuration attributes to stdout.
        """
        prefix = "    " * indent
        has_output = False
        for name in dir(cls):
            if name.startswith("_") or callable(getattr(cls, name)):
                continue
            value = getattr(cls, name)
            has_output = True
            if isinstance(value, type) and issubclass(value, ConfigBase):
                print(f"{prefix}{name}:")
                value.check(indent + 1)
            else:
                print(f"{prefix}{name} = {repr(value)}")

        if not has_output:
            print(f"{prefix}No configuration attributes found")
