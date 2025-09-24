import json
import os
import shutil
from typing import Any, Dict, Union
import uuid

from numpy import copy

from omd2tex.tools.settings_preamble import SettingsPreamble


from .citation import Citation
from .makefile import Makefile
from .paragraph import Paragraph
from .preamble import Preamble
from .file import File
from .quote import Quote
from ..tools import Global
from ..tools import Settings


class Document:
    def __init__(
        self,
        filename: str = "",
        settings: Union[Dict[str, Any], str] = None,
        preamble=os.path.join(os.getcwd(), "../default/preamble.json"),
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

        export = os.path.expanduser(Settings.Export.export_dir)
        search = os.path.expanduser(Settings.Export.search_dir)
        Settings.Export.search_ignore_dirs.append(os.path.relpath(export, search))

    def from_file(self, filename: str):
        self.filename = filename
        Global.DOCUMENT_NAME = self.filename.strip(".md")
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )
        file.from_file(filename)
        self.file = file
        return self

    def from_text(self, text: str):
        self.filename = str(uuid.uuid4())[0:7]
        Global.DOCUMENT_NAME = self.filename
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )
        file.from_text(text)
        self.file = file
        return self

    def from_elements(self, list: list):
        self.filename = str(uuid.uuid4())[0:7]
        Global.DOCUMENT_NAME = self.filename

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]

        if not self.dir:
            dir = Settings.Export.export_dir
            self.dir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.strip(".md"),
        )

        dir_depended_classes = [File, Quote]

        for i, el in enumerate(list):
            if isinstance(el, Document):
                raise TypeError(
                    "Can't pass Document to Document.from_elements() function"
                )
            if type(el) in dir_depended_classes:
                if not list[i].parrentdir:
                    list[i].parrentdir += "/" + self.filename.strip(".md")
                list[i].filedepth += 1

        file.from_elements(list)
        self.file = file

        return self

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
{"\\frame{\\titlepage}" if self.preamble.beamer_titlepage and self.preamble else ""}

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
{"\\frame{\\titlepage}" if self.preamble.beamer_titlepage and self.preamble else ""}

{main}

{bibliography}

\\end{{document}}"""

        with open(
            os.path.join(self.dir, self.filename.strip(".md"), "main.tex"), "w"
        ) as f:
            f.write(document)

        if SettingsPreamble.documentclass == "beamer":
            style_json = os.path.join(
                os.path.dirname(__file__), "../default/beamer-themes.json"
            )
            with open(style_json, "r") as f:
                style_dict = json.loads(f.read())
            if SettingsPreamble.Beamer.theme in style_dict:
                style_dir = os.path.join(
                    os.path.dirname(__file__),
                    "../default/beamer-themes/",
                    style_dict[SettingsPreamble.Beamer.theme],
                )
                copy_dir = os.path.join(self.dir, self.filename.strip(".md"))

                shutil.copy2(style_dir, copy_dir)
            else:
                print(f"{SettingsPreamble.Beamer.theme} not found in JSON file")

        Global.to_default()
