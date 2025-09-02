from typing import List
import re


class Quote:
    def __init__(
        self,
        quotelines: List[str],
        filename: str = "",
        parrentdir="",
        filedepth=0,
        quotedepth=0,
    ):
        self.lines = quotelines

        self.parrentdir = parrentdir
        self.filename = filename
        self.quotedepth = quotedepth
        self.filedepth = filedepth

        self.type = None
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
        text = f"""\\begin{{quote}}\\slshape\\noindent
{"\n".join([el.to_latex() for el in self.elements])}
\\end{{quote}}"""

        return self._tabulate_string(text, self.quotedepth - 1)

    def _to_latex_project(self):
        return self.to_latex()

    def _parse_quote_lines(self):
        pattern = re.compile(r"^>\s*!?\[([^\]]+)\]\s*(.*)$")

        new_lines = []
        for i, line in enumerate(self.lines):
            match = pattern.match(line)
            if match and i == 0:
                self.type, self.heading = match.groups()

                if not self.heading:
                    heading = self.type.strip("!")
                    self.heading = heading[0].upper() + heading[1:]
                elif not self.type:
                    self.type = "!default"
                    if not self.heading:
                        self.heading = self.type
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

    def _parse_nested_quote(self):
        pass
