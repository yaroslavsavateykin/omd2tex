import uuid
import os

from .base import BaseClass

from .list import List
from ..tools import Settings
from .quote import Quote


class File(BaseClass):
    def __init__(
        self,
        filename: str = None,
        parrentdir: str = None,
        filedepth: int = 0,
    ) -> None:
        from ..tools import MarkdownParser

        super().__init__()
        self.filename = filename
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
        from ..tools import MarkdownParser

        if not self.parrentdir:
            dir = Settings.Export.export_dir
            self.parrentdir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

        parser = MarkdownParser(
            filename=filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
        )
        parser.from_file(filename)
        if parser.elements:
            self.elements = parser.elements

        return self

    def from_elements(self, list):
        from ..tools import MarkdownParser
        from .document import Document

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]

        if not self.parrentdir:
            dir = Settings.Export.export_dir
            self.parrentdir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

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
                # print(list[i].parrentdir)

                if not list[i].filename:
                    list[i].filename = new_filename
                list[i].parrentdir += "/" + self.filename.replace(".md","")
                list[i].filedepth += 1
                # print(list[i].parrentdir)

        parser.from_elements(list)
        self.elements = parser.elements

        return self

    def from_text(self, text: str):
        from ..tools import MarkdownParser

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]

        if not self.parrentdir:
            dir = Settings.Export.export_dir
            self.parrentdir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

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
                filename_tex = self.filename.replace(".md","") + ".tex"
            else:
                filename_tex = "main.tex"

            with open(self.parrentdir + "/" + filename_tex, "w") as f:
                f.write(text)
            return f"\\input{{{filename_tex}}}"
