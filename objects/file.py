from objects.list import List
from tools.markdown_parser import MarkdownParser
from tools.settings import Settings
from .reference import Reference


class File:
    def __init__(
        self,
        filename: str,
        parrentfilename: str = "",
        parrentdir: str = "",
        filedepth: int = 0,
    ) -> None:
        self.filename = filename
        self.parrentfilename = parrentfilename
        self.parrentdir = parrentdir
        self.filedepth = filedepth

        self.elements = File._process_elements_list(
            MarkdownParser(
                filename=filename,
                parrentdir=parrentdir,
                filedepth=filedepth,
            ).parse()
        )

    def check(self):
        elements = self.elements
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    @staticmethod
    def _process_elements_list(elements: list) -> list:
        elements = Reference.attach_reference(elements)
        elements = Reference.identify_elements_reference(elements)
        elements = List.append_items(elements)
        elements = List.merge_items(elements)

        return elements

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
