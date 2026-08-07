import re

from .base import BaseClass

class Citation(BaseClass):
    citation_list = []

    def __init__(self, key: str) -> None:
        """Initialize citation metadata and resolve bibtex content.

        Args:
            key: Citation key (may include @) used to locate markdown source.

        Returns:
            None

        Side Effects:
            Sets global citation initialization flag and appends to class registry.
        """

        from ..tools import Global
        super().__init__()
        self.key = key
        self.text = self._found_citation()
        if self.text:
            Global.CITATION_INITIALIZED = True
            self.__class__.citation_list.append(self)

    def _found_citation(self) -> str:
        """Locate and parse citation text from a markdown file."""
        from ..tools import find_file
        from ..tools import Settings
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
    def _parse_citation(text: str) -> str:
        """Normalize raw citation text extracted from markdown."""
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
            text = text.replace(obj, "")

        text = re.sub(
            r"(?<=\S),(?=\S)", " and ", text
        )  # фикс бага плагина Bibtex manager, который почему то убирает " and " и заменяет на запятую

        text = text.replace("_", "\\_").replace("–", "--").replace(" &", " \\&")

        return text

    def to_latex(self) -> str:
        """Render citation content into LaTeX filecontents and bibliography declaration."""
        text = ""
        if self.text:
            key = self.key.removesuffix(".md").lstrip("@")

            text = f"""\\begin{{filecontents*}}{{{key}.bib}}
{self.text}
\\end{{filecontents*}}
\\addbibresource{{{key}.bib}}"""

        return text

    @classmethod
    def to_latex_preamble(cls) -> str:
        """Concatenate LaTeX preamble entries for all registered citations."""
        unique_citations = {}
        for citation in cls.citation_list:
            unique_citations.setdefault(citation.key, citation)
        citation_text = "\n\n".join(
            citation.to_latex() for citation in unique_citations.values()
        )

        return citation_text
