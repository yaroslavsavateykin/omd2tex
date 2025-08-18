import json
import os
import shutil
from typing import Any, Dict, Union


from objects import citation
from objects.citation import Citation
from objects.paragraph import Paragraph
from objects.preamble import Preamble
from objects.file import File
from tools.globals import Global
from tools.settings import Settings


class Document:
    def __init__(
        self,
        filename: str,
        settings: Union[Dict[str, Any], str] = None,
        preamble="default/preamble.json",
    ):
        self.filename = filename

        if settings:
            Settings.update(settings)

        dir = Settings.Export.export_dir
        dir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)
        self.dir = dir

        if Settings.Preamble.create_preamble:
            with open(preamble, "r") as f:
                self.preamble = Preamble()
        else:
            self.preamble = Paragraph("")

    def check(self):
        File(
            self.filename,
            parrentdir=self.dir,
            parrentfilename=self.filename,
        ).check()

        Global.check()
        Global.to_default()

    def _process_settings_logics(self):
        pass

    def to_latex(self):
        preamble = self.preamble.to_latex()

        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename
        file = File(
            self.filename,
            parrentdir=self.dir,
        ).to_latex()

        if Global.CITATION_INITIALIZED:
            citations = Citation.to_latex_preamble()
            bibliography = "\\newpage\\printbibliography"
        else:
            citations = ""
            bibliography = ""

        document = rf"""
{preamble}

{citations}

\begin{{document}}

{file}

{bibliography}

\end{{document}}"""

        Global.to_default()
        return document

    def to_latex_file(self, filename: str = "") -> None:
        file = self.to_latex()

        if not filename:
            filename = self.filename.strip(".md") + ".tex"

        # with open(os.getcwd() + "/" + filename, "w") as f:

        with open(self.dir + "/" + self.filename.strip(".md"), "w") as f:
            f.write(file)

        if Settings.Export.makefile:
            shutil.copy2("default/Makefile", dir)

        Global.to_default()

    def to_latex_porject(self, filename="") -> None:
        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename

        main = File(
            self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )

        try:
            os.makedirs(self.dir + "/" + self.filename.strip(".md"))
        except:
            # print("Не удалось создать директорию проекта или она уже создана")
            pass

        if Settings.Export.makefile:
            shutil.copy2(
                "default/Makefile", self.dir + "/" + self.filename.strip(".md")
            )

        if Global.CITATION_INITIALIZED:
            citations = Citation.to_latex_preamble()
            bibliography = "\\newpage\\printbibliography"
        else:
            citations = ""
            bibliography = ""

        document = f"""
{self.preamble.to_latex_project()}

{citations}

\\begin{{document}}

{main.to_latex_project()}

{bibliography}

\\end{{document}}"""

        with open(
            self.dir + "/" + self.filename.strip(".md") + "/" + "main.tex", "w"
        ) as f:
            f.write(document)

        Global.to_default()
