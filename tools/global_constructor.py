from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import Dict, Any, Optional, Union
import json


@dataclass_json
@dataclass
class ConfigBase:
    def check(self, indent=0):
        prefix = "    " * indent
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, ConfigBase):
                print(f"{prefix}{field_name}:")
                field_value.check(indent + 1)
            else:
                print(f"{prefix}{field_name} = {repr(field_value)}")

    def update(self, new_settings: Union[Dict[str, Any], str]):
        if isinstance(new_settings, str):
            with open(new_settings, "r") as f:
                new_settings = json.load(f)

        for key, value in new_settings.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, ConfigBase) and isinstance(value, dict):
                    current_value.update(value)
                else:
                    setattr(self, key, value)


def create_config_class(class_name: str, settings: Union[Dict[str, Any], str]):
    """Динамически создает dataclass с вложенными структурами"""
    fields = {}
    defaults = {}

    if isinstance(settings, str):
        with open(settings, "r") as f:
            settings = json.load(f)
    elif isinstance(settings, dict):
        pass
    else:
        raise TypeError("Settings are either a string or a dictionary")

    for key, value in settings.items():
        if isinstance(value, dict):
            # Рекурсивно создаем вложенный класс
            nested_class = create_config_class(f"{key.capitalize()}Config", value)
            fields[key] = field(
                default_factory=nested_class, metadata=config(field_name=key)
            )
            defaults[key] = nested_class()
        else:
            fields[key] = field(default=value, metadata=config(field_name=key))
            defaults[key] = value

    # Создаем dataclass
    new_class = dataclass(
        type(
            class_name,
            (ConfigBase,),
            {"__annotations__": {k: type(v) for k, v in defaults.items()}},
        )
    )

    # Устанавливаем значения по умолчанию
    new_class.__dataclass_fields__ = fields
    return new_class
