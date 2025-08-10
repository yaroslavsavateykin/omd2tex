from tools.search import find_file
from .markdownparser import MarkdownParser
from tools.attach_reference import attach_reference


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

        self.elements = MarkdownParser(filename, settings, parrentdir, depth).parse()

    def to_latex(self, settings={}):
        # print(len(self.elements))
        print(self.elements)
        elements = attach_reference(self.elements)

        # print(len(elements))

        text = "\n\n".join([elem.to_latex(self.settings) for elem in elements])

        return text

    def to_latex_project(self, settings={}) -> str:
        elements = attach_reference(self.elements)

        if self.settings["branching_project"]:
            pass
        else:
            # print(self.elements)
            text = "\n\n".join(
                [elem.to_latex_project(self.settings) for elem in elements]
            )

            if self.filename:
                filename_tex = self.filename.strip(".md") + ".tex"
            else:
                filename_tex = "main.tex"

            with open(self.parrentdir + "/" + filename_tex, "w") as f:
                f.write(text)
            return f"\\include{{{filename_tex}}}"
