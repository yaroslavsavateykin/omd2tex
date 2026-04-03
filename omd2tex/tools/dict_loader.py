import json
from typing import Dict


class DictLoader:
    def __init__(self, type="default"):
        self.type = type
        self.loaded = False
        self.dict = {}
        self.filename = ""
        self.str_dict = ""

    def load_dict(self, dict_data):
        self.dict = dict_data
        self.loaded = True

        return self

    def load_json_file(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            self.dict = json.loads(f.read())

        self.filename = filename
        self.loaded = True

        return self

    def to_obs_dict(self):
        def recursive_construct(dict_data: Dict):
            new_dict = {}
            for key1 in dict_data:
                if isinstance(key1, str):
                    if isinstance(dict_data[key1], Dict):
                        for key2 in dict_data[key1]:
                            if isinstance(key2, str):
                                new_dict[f"{key1}.{key2}"] = dict_data[key1][key2]
                            else:
                                new_dict[key1][key2] = dict_data[key1][key2]
                    else:
                        new_dict[key1] = dict_data[key1]
                else:
                    new_dict[key1] = dict_data[key1]

            if any(isinstance(new_dict[key], Dict) for key in new_dict):
                return recursive_construct(new_dict)
            else:
                return new_dict

        if self.loaded:
            self.dict = recursive_construct(self.dict)

        self.type = "obsidian"

        return self

    def from_obs_dict(self):
        def recursive_reconstruct(dict_data):
            new_dict = {}

            for key, value in dict_data.items():
                if isinstance(key, str) and "." in key:
                    key_parts = key.split(".")
                    current_dict = new_dict

                    for part in key_parts[:-1]:
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]

                    current_dict[key_parts[-1]] = value
                else:
                    new_dict[key] = value

            for key, value in new_dict.items():
                if isinstance(value, dict):
                    new_dict[key] = recursive_reconstruct(value)

            return new_dict

        if self.loaded:
            self.dict = recursive_reconstruct(self.dict)

        self.type = "default"

        return self
