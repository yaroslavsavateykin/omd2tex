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
    ) -> None:
        """Initialize a quote block with nested markdown parsing.

        Args:
            quotelines: Lines comprising the quote.
            filename: Source filename for context.
            parrentdir: Parent directory path for resolving includes.
            filedepth: Current depth of file recursion.
            quotedepth: Current depth of nested quotes.

        Returns:
            None
        """
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
    def _tabulate_string(string: str, level: int) -> str:
        """Indent each line of a string by a specified level.

        Args:
            string: Input multiline string.
            level: Number of indentation levels (each equals four spaces).

        Returns:
            Indented string.
        """
        new_string = []
        for line in string.splitlines():
            line = "    " * level + line
            new_string.append(line)

        return "\n".join(new_string)

    def to_latex(self) -> str:
        """Convert the quote and its elements to LaTeX.

        Args:
            None

        Returns:
            LaTeX string for the quote environment with proper indentation.
        """
        text = "\\\\\n".join([el.to_latex() for el in self.elements])

        text = f"""\\begin{{quote}}\\slshape\\noindent
{text}
\\end{{quote}}"""

        return self._tabulate_string(text, self.quotedepth - 1)

    def _to_latex_project(self) -> str:
        return self.to_latex()

    def _parse_quote_lines(self) -> None:
        """Parse quote lines to determine quote type and nested elements.

        Args:
            None

        Returns:
            None

        Side Effects:
            Populates quote metadata and element list.
        """
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
    ) -> BaseClass:
        """Factory to create and process quote content in one step.

        Args:
            quotelines: Raw quote lines including leading markers.
            filename: Source filename for context.
            parrentdir: Parent directory path for nested includes.
            filedepth: Current file recursion depth.
            quotedepth: Current quote recursion depth.

        Returns:
            Processed element resulting from quote interpretation.
        """
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

    def _apply_quote_type(self) -> BaseClass:
        """Apply quote-specific rendering rules and return a replacement element.

        Args:
            None

        Returns:
            Appropriate element corresponding to quote type, defaulting to a quoted paragraph.
        """
        text = "\n\n".join([el.to_latex() for el in self.elements])

        functions = {
            "example": lambda content: Paragraph(
                "\\begin{example}\n" + "\n".join(content) + "\n\\end{example}"
            ),
            "hidden": lambda content: Paragraph("", parse=False),
            "text": lambda content: Paragraph(content, parse=False),
            "task": lambda content: Paragraph(
                f"\\begin{{breakableframe}}\n{content}\n\\end{{breakableframe}}",
                parse=False,
            ),
            "solution": lambda content: Paragraph(content, parse=False),
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
        """Fallback quote rendering when no specialized type is matched.

        Args:
            text: Raw text content to wrap in a quote environment.

        Returns:
            Paragraph element containing the default quote representation.
        """
        text = f"""\\begin{{quote}}\\slshape\\noindent
{text}
\\end{{quote}}"""
        return Paragraph(text, parse=False)
