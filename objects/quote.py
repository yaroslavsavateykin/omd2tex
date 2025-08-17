from typing import List
import re


class Quote:
    def __init__(
        self,
        quotelines: List[str],
        settings: dict = {},
        filename: str = "",
        parrentfilename: str = "",
        parrentdir="",
        filedepth=0,
        quotedepth=0,
    ):
        self.lines = quotelines
        self.settings = settings

        self.type = None
        self.heading = None
        self._parse_quote_lines()

        self.reference = None

        self.parrentfilename = parrentfilename
        self.parrentdir = parrentdir
        self.filename = filename
        self.quotedepth = quotedepth
        self.filedepth = filedepth

        from objects.file import File
        from tools.markdown_parser import MarkdownParser

        self.elements = File._process_elements_list(
            MarkdownParser(
                settings=settings,
                filename=filename,
                parrentdir=parrentdir,
                filedepth=filedepth,
                quotedepth=quotedepth,
            ).parse(self.lines)
        )

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
\\end{{quote}}\\vspace{{-\\baselineskip}}"""

        return self._tabulate_string(text, self.quotedepth - 1)

    def to_latex_project(self):
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

        self.lines = new_lines

    def _parse_nested_quote(self):
        pass
