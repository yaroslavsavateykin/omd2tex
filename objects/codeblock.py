from .paragraph import Paragraph


class CodeBlock:
    def __init__(self, blocktype: str, blocklines: list, settings={}) -> None:
        self.blocktype = blocktype
        self.blocklines = blocklines

        if settings:
            self.settings = settings
        else:
            self.settings = {}

        self.reference = None

    @staticmethod
    def _minted_python(blocklines: list):
        block = f"""
\\usemintedstyle{{default}}")
\\begin{{minted}}[mathescape, linenos, numbersep=5pt, frame=lines, framesep=2mm, breaklines]{{python}}") 
{"\n".join(blocklines)}
\\end{{minted}}
"""
        return Paragraph(block)

    @staticmethod
    def _default_codeblock(blocklines: list):
        block = f"""
\\begin{{tcolorbox}}[colback=gray!20, colframe=gray!50, sharp corners, boxrule=1pt]
\\begin{{verbatim}}
{"\n".join(blocklines)}
\\end{{verbatim}}
\\end{{tcolorbox}}
"""
        return Paragraph(block)

    def _apply_blocktype(self):
        functions = {
            "example": lambda content: Paragraph(
                f"\\begin{{example}}\n{'\n'.join(content)}\n\\end{{example}}"
            ),
            "hidden": lambda content: Paragraph(""),
            "text": lambda content: Paragraph("\n".join(content)),
            "python": self._minted_python,
            "c": self._minted_python,
            "cpp": self._minted_python,
            "c++": self._minted_python,
            "java": self._minted_python,
            "bash": self._minted_python,
        }
        if self.blocktype in functions:
            return functions[self.blocktype](self.blocklines)
        else:
            return self._default_codeblock(self.blocklines)

    def to_latex(self, settings={}):
        return self._apply_blocktype().to_latex()

    def to_latex_project(self, settings={}):
        return self.to_latex(settings)
