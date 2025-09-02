import re

from ..tools import Global
from ..tools import find_file
from ..tools import Settings


class Citation:
    citation_list = []

    def __init__(self, key):
        Global.CITATION_INITIALIZED = True

        self.key = key
        self.text = self._found_citation()
        self.__class__.citation_list.append(self)

    def _found_citation(self):
        path = find_file(
            filename=self.key + ".md", search_path=Settings.Export.search_dir
        )

        if path:
            with open(path, "r") as f:
                text = self._parse_citation(f.read())
        else:
            print(f"Citation {self.key} not found")
            text = ""

        return text

    @staticmethod
    def _parse_citation(text):
        objects = [
            r"{{title}}",
            r"{{author}}",
            r"{{journal}}",
            r"{{number}}",
            r"{{volume}}",
            r"{{pages}}",
            r"{{year}}",
        ]

        text = text.replace("```", "").replace("bibtex", "")

        for obj in objects:
            text.replace(obj, "")

        text = re.sub(
            r"(?<=\S),(?=\S)", " and ", text
        )  # фикс бага плагина Bibtex manager, который почему то убирает " and " и заменяет на запятую

        text = text.replace("_", "\\_").replace("–", "--").replace(" &", " \\&")

        return text

    def to_latex(self):
        if self.text:
            key = self.key.strip(".md").strip("@")

            text = f"""\\begin{{filecontents*}}{{{key}.bib}}
{self.text}
\\end{{filecontents*}}
\\addbibresource{{{key}.bib}}"""

        return text

    @classmethod
    def to_latex_preamble(cls):
        citation_text = "\n\n".join(cit.to_latex() for cit in cls.citation_list)

        return citation_text
