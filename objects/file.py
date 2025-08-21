import uuid

from objects.list import List
from tools.markdown_parser import MarkdownParser
from tools.settings import Settings
from objects.quote import Quote


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
            ).from_file(filename)
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

        return self

    def from_elements(self, list):
        from objects.document import Document

        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )

        dir_depended_classes = [File, Quote]

        for i, el in enumerate(list):
            if isinstance(el, Document):
                raise TypeError("Can't pass Document to File.from_elements() function")

            new_filename = str(uuid.uuid4())[0:7]

            if type(el) in dir_depended_classes:
                if not list[i].filename:
                    list[i].filename = new_filename
                if not list[i].parrentfilename:
                    list[i].parrentfilename = self.filename
                if not list[i].parrentdir:
                    list[i].parrentdir = (
                        self.parrentdir + "/" + self.filename.strip(".md")
                    )
                list[i].filedepth += 1

        parser.from_elements(list)
        self.elements = parser.elements

        return self

    def from_text(self, text: str):
        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )
        parser.from_text(text)
        self.elements = parser.elements

        return self

    def check(self):
        elements = self.elements
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    def to_latex(self):
        text = "\n\n".join([elem.to_latex() for elem in self.elements])

        return text

    def _to_latex_project(self) -> str:
        if Settings.Export.branching_project:
            pass
        else:
            # print(self.elements)
            text = "\n\n".join([elem._to_latex_project() for elem in self.elements])

            if self.filename:
                filename_tex = self.filename.strip(".md") + ".tex"
            else:
                filename_tex = "main.tex"

            with open(self.parrentdir + "/" + filename_tex, "w") as f:
                f.write(text)
            return f"\\input{{{filename_tex}}}"
