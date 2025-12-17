from typing import Dict, Optional, Union, List
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
        """Safely quote time-like YAML fields to preserve strings.

        Wraps values for keys ``startTime``, ``endTime``, and ``date`` in quotes so ``yaml.safe_load`` does not coerce them to numeric or timestamp types.

        Args:
            yaml_text: Raw YAML frontmatter text.

        Returns:
            YAML text with targeted values quoted.

        Raises:
            None explicitly.
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

    def __init__(self, filename: Optional[str] = None, abs_path: Optional[str] = None, text: Union[List[str], str] = "") -> None:
        """Parse YAML frontmatter from filename, absolute path, or text.

        Determines whether frontmatter exists, extracts it, optionally loads from disk, and stores parsed YAML along with the line index where frontmatter ends.

        Args:
            filename: Optional relative filename to locate and read.
            abs_path: Optional absolute path to read directly.
            text: Raw markdown content as lines or a single string.

        Returns:
            None

        Raises:
            FileNotFoundError: If provided files cannot be read.
            yaml.YAMLError: Propagated when YAML parsing fails.
        """
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

    def update(self, new_dict: Dict) -> "FrontMatterParser":
        """Update the stored YAML dictionary with new keys and values.

        Args:
            new_dict: Mapping of keys to merge into the existing YAML data.

        Returns:
            Self instance after update.
        """
        self.yaml.update(new_dict)

        return self

    def update_file(self, new_dict: Dict = {}) -> None:
        """Persist updated YAML back to the associated file.

        Merges new data into the current YAML, reconstructs the file with the updated frontmatter, and writes it to disk.

        Args:
            new_dict: Optional mapping of additional values to merge before writing.

        Returns:
            None

        Raises:
            FileNotFoundError: If the target file is missing.
            IOError: Propagated on write failures.
        """
        self.update(new_dict)

        with open(self.abs_path, "r") as f:
            text = f.read().splitlines()[self.yaml_line_end :]

        dump = yaml.dump(self.yaml, allow_unicode=True, sort_keys=False)
        new_file = f"---\n{dump}---\n" + "\n".join(text)

        # print(new_file)

        with open(self.abs_path, "w") as f:
            f.write(new_file)
