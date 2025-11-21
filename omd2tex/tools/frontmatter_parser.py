import yaml

from omd2tex.objects import file

from .search import find_file


class FrontMatterParser:
    def __init__(self, filename: str = "", text: str = ""):
        if filename:
            self.filename = filename
            abs_path = find_file(filename)

        in_frontmatter = False

        if filename:
            with open(abs_path, "r") as f:
                text = f.read()

        if text.startswith("---"):
            in_frontmatter = True

        yaml_lines = []
        text = text.splitlines()
        i = 0

        while in_frontmatter:
            line = text[i]

            if line.startswith("---"):
                in_frontmatter = False
            else:
                yaml_lines.append(line)

            i += 1

        self.yaml = yaml.safe_load("\n".join(yaml_lines))
