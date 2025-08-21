from typing import List
from pylatexenc.latex2text import LatexNodes2Text
import numpy as np

from tools.globals import Global
from objects.paragraph import Paragraph


class Table:
    def __init__(self, lines: List[str]):
        self.lines = lines

        self.ilen = 2
        self.jlen = 2
        self.alignments = []
        self.width_parms = self._define_width_parms()
        self.colspec = self._define_colspec_parms()

        self.reference = None
        self.caption = None

        self._is_initialized = True

    def _identify_reference(self):
        self._is_initialized = True
        Global.REFERENCE_DICT[self.reference] = "tab"

    def to_latex(self):
        if not self._is_initialized:
            raise RuntimeError(
                "Table is not initialized! Firstly call _identify_reference()"
            )

        return self._to_longtblr()

    def _to_latex_project(self):
        return self.to_latex()

    def _parse_lines(self) -> str:
        new_lines = []
        for i, line in enumerate(self.lines):
            line = [Paragraph(x).to_latex() for x in line.strip("|").strip().split("|")]
            if i == 1:
                for box in line:
                    box = box.strip()
                    if box.startswith(":"):
                        self.alignments.append("l")
                    elif box.startswith(":") and box.endswith(":"):
                        self.alignments.append("c")
                    elif box.endswith(":"):
                        self.alignments.append("r")
                    else:
                        self.alignments.append("c")
                continue
            new_lines.append(line)

        return new_lines

    @staticmethod
    def _convert_to_latex_symbols(line: str):
        latex_line = (
            LatexNodes2Text()
            .latex_to_text(line)
            .replace(" ", "")
            .replace("_", "")
            .replace("\n", "")
        )
        # print(f"Conversion: {line} -> {latex_line}")

        return latex_line

    def _define_width_parms(self):
        lines = self._parse_lines()

        symbol_lines = []

        for line in lines:
            symbol_line = [len(self._convert_to_latex_symbols(x)) for x in line]

            symbol_lines.append(symbol_line)

        self.ilen = len(symbol_lines[0])
        self.jlen = len(symbol_lines)

        width_parms = np.array(symbol_lines, dtype=float).max(axis=0)

        return width_parms

    def _define_colspec_parms(self):
        colspec = ""
        if (
            self.ilen > 6
            or (self.ilen > 3 and np.max(self.width_parms) > 20)
            or np.max(self.width_parms) > 30
        ):
            for i, al in enumerate(self.alignments):
                colspec += f"X[{self.width_parms[i]},{al}]"
        else:
            for i, al in enumerate(self.alignments):
                colspec += f"Q[{al}]"

        return colspec

    def _to_longtblr(self):
        lines = self._parse_lines()

        if self.reference:
            reference = f"label={{tab:{self.reference}}},"
        else:
            reference = ""

        if self.caption:
            caption = f"caption={{{self.caption}}}"
        else:
            caption = ""

        new_lines = ""
        for line in lines:
            line = " & ".join(line) + "\\\\"
            new_lines += line + "\n"

        string = f"""
\\begingroup
\\centering
\\begin{{longtblr}}[{reference} {caption}]{{colspec={{{self.colspec}}}, hlines,vlines}}
{new_lines}
\\end{{longtblr}}
\\endgroup
"""
        return string
