from objects.globals import Global
from objects.headline import Headline
from tools.search import find_file
from .markdownparser import MarkdownParser
from .reference import Reference


class File:
    def __init__(
        self,
        filename: str,
        settings: dict,
        depth: int = 0,
        parrentfilename: str = "",
        parrentdir: str = "",
    ) -> None:
        self.filename = filename
        self.parrentfilename = parrentfilename
        self.parrentdir = parrentdir
        self.settings = settings
        self.depth = depth

        self.elements = File._process_elements_list(
            MarkdownParser(filename, settings, parrentdir, depth).parse()
        )

    def check(self):
        elements = self.elements
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    @staticmethod
    def _process_elements_list(elements: list) -> list:
        elements = Reference.attach_reference(elements)
        elements = Reference.identify_elements_reference(elements)

        return elements

    def to_latex(self):
        text = "\n\n".join([elem.to_latex() for elem in self.elements])

        return text

    def to_latex_project(self) -> str:
        if self.settings["branching_project"]:
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
