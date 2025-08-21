import json
import os
import shutil
from typing import Any, Dict, Union
import uuid


from objects import citation
from objects.citation import Citation
from objects.makefile import Makefile
from objects.paragraph import Paragraph
from objects.preamble import Preamble
from objects.file import File
from objects.quote import Quote
from tools.globals import Global
from tools.settings import Settings


class Document:
    def __init__(
        self,
        filename: str = "",
        settings: Union[Dict[str, Any], str] = None,
        preamble="default/preamble.json",
    ):
        if settings:
            Settings.update(settings)

        dir = Settings.Export.export_dir
        self.dir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

        self.filename = filename
        self.file = None

        if Settings.Preamble.create_preamble:
            self.preamble = Preamble()
        else:
            self.preamble = Paragraph("")

    def from_file(self, filename: str):
        self.filename = filename
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )
        file.from_file(filename)
        self.file = file

    def from_text(self, text: str):
        self.filename = str(uuid.uuid4())[0:7]
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )
        file.from_text(text)
        self.file = file

    def from_elements(self, list: list):
        self.filename = str(uuid.uuid4())[0:7]

        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )

        dir_depended_classes = [File, Quote]

        for i, el in enumerate(list):
            if isinstance(el, Document):
                raise TypeError(
                    "Can't Document class to Document.from_elements() function"
                )
            """
            new_filename = str(uuid.uuid4())[0:7]

            if type(el) in dir_depended_classes:
                if not list[i].filename:
                    list[i].filename = new_filename
                if not list[i].parrentfilename:
                    list[i].parrentfilename = self.filename
                if not list[i].parrentdir:
                    list[i].parrentdir = self.dir + "/" + self.filename.strip(".md")
                list[i].filedepth += 1
            """

        file.from_elements(list)
        self.file = file

    def _process_settings_logics(self):
        pass

    def check(self):
        if self.file:
            self.file.check()
        else:
            print("Document is not initialized")

        Global.check()
        Global.to_default()

    def to_latex(self):
        preamble = self.preamble.to_latex()

        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename
        file = self.file.to_latex()

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
            Makefile.to_file(dir)

        Global.to_default()

    def to_latex_project(self, filename="") -> None:
        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename

        if not self.filename or not self.file:
            raise ValueError("Document must be initialized")

        if self.file:
            main = self.file
        else:
            raise ValueError("Document is not initialized")

        try:
            os.makedirs(self.dir + "/" + self.filename.strip(".md"))
        except:
            # print("Не удалось создать директорию проекта или она уже создана")
            pass

        main = main._to_latex_project()

        if Settings.Export.makefile:
            Makefile.to_file(self.dir + "/" + self.filename.strip(".md"))

        if Global.CITATION_INITIALIZED:
            citations = Citation.to_latex_preamble()
            bibliography = "\\newpage\\printbibliography"
        else:
            citations = ""
            bibliography = ""

        document = f"""
{self.preamble._to_latex_project()}

{citations}

\\begin{{document}}

{main}

{bibliography}

\\end{{document}}"""

        with open(
            self.dir + "/" + self.filename.strip(".md") + "/" + "main.tex", "w"
        ) as f:
            f.write(document)

        Global.to_default()
