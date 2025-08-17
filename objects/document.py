import json
import os
import shutil

from objects.paragraph import Paragraph

from objects.preamble import Preamble
from objects.file import File
from tools.globals import Global


class Document:
    def __init__(
        self,
        filename: str,
        settings="default/settings.json",
        preamble="default/preamble.json",
    ):
        with open(settings, "r") as f:
            self.settings = json.load(f)

        self.filename = filename

        dir = self.settings["output_dir"]
        dir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)
        self.dir = dir

        if self.settings["preamble"]:
            with open(preamble, "r") as f:
                self.preamble = Preamble(json.load(f), parrentdir=self.dir)
        else:
            self.preamble = Paragraph("")

    def check(self):
        File(
            self.filename,
            self.settings,
            parrentdir=self.dir,
            parrentfilename=self.filename,
        ).check()

        Global.check()
        Global.clear()

    def _process_settings_logics(self):
        pass

    def to_latex(self):
        preamble = self.preamble.to_latex()

        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename
        file = File(
            self.filename,
            self.settings,
            parrentdir=self.dir,
        ).to_latex()

        document = rf"""
{preamble}

\begin{{document}}

{file}

\end{{document}}"""

        Global.clear()
        return document

    def to_latex_file(self, filename: str = "") -> None:
        file = self.to_latex()

        if not filename:
            filename = self.filename.strip(".md") + ".tex"

        # with open(os.getcwd() + "/" + filename, "w") as f:

        with open(self.dir + "/" + self.filename.strip(".md"), "w") as f:
            f.write(file)

        if self.settings["makefile"]:
            shutil.copy2("default/Makefile", dir)

        Global.clear()

    def to_latex_porject(self, filename="") -> None:
        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename

        main = File(
            self.filename,
            self.settings,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )

        try:
            os.makedirs(self.dir + "/" + self.filename.strip(".md"))
        except:
            # print("Не удалось создать директорию проекта или она уже создана")
            pass

        shutil.copy2("default/Makefile", self.dir + "/" + self.filename.strip(".md"))

        document = f"""
{self.preamble.to_latex_project()}

\\begin{{document}}

{main.to_latex_project()}

\\end{{document}}"""

        with open(
            self.dir + "/" + self.filename.strip(".md") + "/" + "main.tex", "w"
        ) as f:
            f.write(document)

        Global.clear()
