from typing import Dict, Union, List
import yaml
import re
from collections import OrderedDict


for ch, resolvers in list(yaml.SafeLoader.yaml_implicit_resolvers.items()):
    yaml.SafeLoader.yaml_implicit_resolvers[ch] = [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


class FrontMatterParser:
    @staticmethod
    def quote_sensitive_yaml_values(yaml_text: str) -> str:
        """
        Добавляет кавычки к значениям для ключей startTime, endTime, date,
        чтобы safe_load не превращал их в числа или timestamp.
        """
        patterns = {
            r"^(startTime:\s*)([0-9]{1,2}:[0-9]{2})$",
            r"^(endTime:\s*)([0-9]{1,2}:[0-9]{2})$",
            r"^(date:\s*)([0-9]{4}-[0-9]{2}-[0-9]{2})$",
        }

        lines = yaml_text.splitlines()
        new_lines = []

        for line in lines:
            modified = False
            for pattern in patterns:
                m = re.match(pattern, line)
                if m:
                    key, value = m.groups()
                    line = f'{key}"{value}"'  # ← ДЕЛАЕМ значение строкой
                    modified = True
                    break

            new_lines.append(line)

        return "\n".join(new_lines)

    def __init__(self, filename=None, abs_path=None, text: Union[List[str], str] = ""):
        from .search import find_file

        self.yaml = {}

        in_frontmatter = False

        if isinstance(text, list):
            if text[0].startswith("---"):
                in_frontmatter = True
        elif isinstance(text, str):
            if text.startswith("---"):
                in_frontmatter = True
            text = text.splitlines()

        if filename:
            self.filename = filename
            self.abs_path = abs_path
            abs_path = find_file(filename)

            with open(abs_path, "r") as f:
                text = f.read()
                if text.startswith("---"):
                    in_frontmatter = True
                    text = text.splitlines()

        if abs_path:
            self.abs_path = abs_path
            with open(abs_path, "r") as f:
                text = f.read()
                if text.startswith("---"):
                    in_frontmatter = True
                    text = text.splitlines()

        yaml_lines = []

        i = 1
        j = 0

        while in_frontmatter:
            line = text[i]

            i += 1

            if line.startswith("---"):
                in_frontmatter = False
                j = i
            else:
                yaml_lines.append(line)

        # print(yaml_lines)
        if yaml_lines:
            yaml_lines = "\n".join(yaml_lines)
            yaml_lines = self.quote_sensitive_yaml_values(yaml_lines)
            self.yaml = yaml.safe_load(yaml_lines)
        self.yaml_line_end = j

    def update(self, new_dict: Dict):
        self.yaml.update(new_dict)

        return self

    def update_file(self, new_dict: Dict = {}):
        self.update(new_dict)

        with open(self.abs_path, "r") as f:
            text = f.read().splitlines()[self.yaml_line_end :]

        dump = yaml.dump(self.yaml, allow_unicode=True, sort_keys=False)
        new_file = f"---\n{dump}---\n" + "\n".join(text)

        # print(new_file)

        with open(self.abs_path, "w") as f:
            f.write(new_file)
