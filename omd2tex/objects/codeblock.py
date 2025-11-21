from .base import BaseClass
from .fragment import Caption
from .paragraph import Paragraph


class CodeBlock(BaseClass):
    def __init__(self, blocktype: str, blocklines: list) -> None:
        super().__init__()
        self.blocktype = blocktype
        self.blocklines = blocklines
        self.reference = None

    @staticmethod
    def _minted_python(blocklines: list):
        block = f"""\\usemintedstyle{{default}}
\\begin{{minted}}[mathescape, linenos, numbersep=5pt, frame=lines, framesep=2mm, breaklines]{{python}} 
{"\n".join(blocklines)}
\\end{{minted}}"""

        return Paragraph(block, parse=False)

    @staticmethod
    def _default_codeblock(blocklines: list):
        block = f"""\\begin{{tcolorbox}}[colback=gray!20, colframe=gray!50, sharp corners, boxrule=1pt]
\\begin{{verbatim}}
{"\n".join(blocklines)}
\\end{{verbatim}}
\\end{{tcolorbox}}"""

        return Paragraph(block, parse=False)

    def _apply_blocktype(self):
        functions = {
            "example": lambda content: Paragraph(
                f"\\begin{{example}}\n{'\n'.join(content)}\n\\end{{example}}"
            ),
            "hidden": lambda content: Paragraph("", parse=False),
            "text": lambda content: Paragraph("\n".join(content)),
            "caption": lambda content: Caption(" ".join(content)),
            "pause": lambda content: Paragraph("\\pause", parse=False),
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

    @classmethod
    def create(cls, blocktype: str, blocklines: list):
        instance = cls.__new__(cls)
        instance.blocktype = blocktype
        instance.blocklines = blocklines
        instance.reference = None
        return instance._apply_blocktype()

    def to_latex(self):
        return self._apply_blocktype().to_latex()

    def _to_latex_project(self):
        return self.to_latex()
