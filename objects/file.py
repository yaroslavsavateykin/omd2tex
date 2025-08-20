from objects.list import List
from tools.markdown_parser import MarkdownParser
from tools.settings import Settings


class File:
    def __init__(
        self,
        filename: str = None,
        parrentfilename: str = None,
        parrentdir: str = None,
        filedepth: int = 0,
    ) -> None:
        self.filename = filename
        self.parrentfilename = parrentfilename
        self.parrentdir = parrentdir
        self.filedepth = filedepth

        if filename and parrentdir and filedepth:
            parser = MarkdownParser(
                filename=filename,
                parrentdir=parrentdir,
                filedepth=filedepth,
            )
            parser.parse()
            self.elements = parser.elements
        else:
            self.elements = []

    def from_file(self, filename: str):
        parser = MarkdownParser(
            filename=filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )
        parser.from_file(filename)
        self.elements = parser.elements

    def from_elements(self, list):
        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )
        parser.from_elements(list)
        self.elements = parser.elements

    def from_text(self, text: str):
        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )
        parser.from_text(text)
        self.elements = parser.elements

    def check(self):
        elements = self.elements
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    def to_latex(self):
        text = "\n\n".join([elem.to_latex() for elem in self.elements])

        return text

    def to_latex_project(self) -> str:
        if Settings.Export.branching_project:
            pass
        else:
            # print(self.elements)
            text = "\n\n".join([elem.to_latex_project() for elem in self.elements])

            if self.filename:
                filename_tex = self.filename.strip(".md") + ".tex"
            else:
                filename_tex = "main.tex"

            with open(self.parrentdir + "/" + filename_tex, "w") as f:
                f.write(text)
            return f"\\input{{{filename_tex}}}"
