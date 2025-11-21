from typing import List
import re

from .base import BaseClass

from .paragraph import Paragraph
from .fragment import Caption


class Quote(BaseClass):
    def __init__(
        self,
        quotelines: List[str],
        filename: str = "",
        parrentdir="",
        filedepth=0,
        quotedepth=0,
    ):
        super().__init__()
        self.quotelines = quotelines

        self.parrentdir = parrentdir
        self.filename = filename
        self.quotedepth = quotedepth
        self.filedepth = filedepth

        self.quotetype = None
        self.heading = None
        self.elements = []
        self._parse_quote_lines()

        self.reference = None

    @staticmethod
    def _tabulate_string(string: str, level: int):
        new_string = []
        for line in string.splitlines():
            line = "    " * level + line
            new_string.append(line)

        return "\n".join(new_string)

    def to_latex(self):
        text = "\\\\\n".join([el.to_latex() for el in self.elements])

        text = f"""\\begin{{quote}}\\slshape\\noindent
{text}
\\end{{quote}}"""

        return self._tabulate_string(text, self.quotedepth - 1)

    def _to_latex_project(self):
        return self.to_latex()

    def _parse_quote_lines(self):
        pattern = re.compile(r"^>\s*!?\[([^\]]+)\]\s*(.*)$")

        new_lines = []
        for i, line in enumerate(self.quotelines):
            match = pattern.match(line)
            if match and i == 0:
                self.quotetype, self.heading = match.groups()
                self.quotetype = self.quotetype.strip("!")

                if not self.heading:
                    heading = self.quotetype
                    self.heading = heading

                elif not self.quotetype:
                    self.quotetype = "default"
                    if not self.heading:
                        self.heading = self.quotetype
                continue

            new_lines.append(line[1:])

        from ..tools.markdown_parser import MarkdownParser

        self.lines = new_lines

        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
            quotedepth=self.quotedepth,
        )

        parser.from_text(new_lines)

        self.elements = parser.elements

    @classmethod
    def create(
        cls,
        quotelines: List[str],
        filename: str = "",
        parrentdir="",
        filedepth=0,
        quotedepth=0,
    ):
        instance = cls.__new__(cls)
        instance.quotelines = quotelines

        instance.parrentdir = parrentdir
        instance.filename = filename
        instance.quotedepth = quotedepth
        instance.filedepth = filedepth

        instance.quotetype = None
        instance.heading = None
        instance.elements = []
        instance._parse_quote_lines()

        instance.reference = None
        return instance._apply_quote_type()

    def _apply_quote_type(self):
        text = "\\\\\n".join([el.to_latex() for el in self.elements])

        functions = {
            "example": lambda content: Paragraph(
                f"\\begin{{example}}\n{'\n'.join(content)}\n\\end{{example}}"
            ),
            "hidden": lambda content: Paragraph("", parse=False),
            "text": lambda content: Paragraph("\n".join(content)),
            "caption": lambda content: Caption(" ".join(content)),
            "pause": lambda content: Paragraph("\\pause", parse=False),
            "default": lambda content: Paragraph(
                rf"\begin{{quote}}\slshape\noindent\n{text}\n\end{{quote}}", parse=False
            ),
        }
        if self.quotetype in functions:
            return functions[self.quotetype](text)
        else:
            return self._default_quoteline(text)

    @staticmethod
    def _default_quoteline(text: str):
        text = f"""\\begin{{quote}}\\slshape\\noindent
{text}
\\end{{quote}}"""
        return Paragraph(text, parse=False)
