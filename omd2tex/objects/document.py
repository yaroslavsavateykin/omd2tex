import json
import os
import shutil
from typing import Any, Dict, Union
import uuid

from .base import BaseClass

from .citation import Citation
from .makefile import Makefile
from .paragraph import Paragraph
from .preamble import Preamble
from .file import File
from .quote import Quote


class Document(BaseClass):
    def __init__(
        self,
        filename: str = "",
        settings: Union[Dict[str, Any], str] = None,
        preamble=os.path.join(os.getcwd(), "../default/preamble.json"),
    ) -> None:
        """Initialize a document wrapper with optional settings and preamble.

        Args:
            filename: Markdown filename to process.
            settings: Dict or path for overriding settings.
            preamble: Path to preamble configuration JSON.

        Returns:
            None

        Side Effects:
            Updates global settings and search ignore directories.
        """
        from ..tools import SettingsPreamble, Settings, Global

        super().__init__()
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

    def from_file(self, filename: str) -> "Document":
        """Load and parse a markdown file into a Document."""
        from ..tools import SettingsPreamble, Settings, Global

        self.filename = filename
        Global.DOCUMENT_NAME = self.filename.replace(".md", "")
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.replace(".md", ""),
        )
        file.from_file(filename)
        self.file = file
        return self

    def from_text(self, text: str) -> "Document":
        """Create a document from raw markdown text."""
        from ..tools import SettingsPreamble, Settings, Global

        self.filename = str(uuid.uuid4())[0:7]
        Global.DOCUMENT_NAME = self.filename
        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.replace(".md", ""),
        )
        file.from_text(text)
        # file.filename = self.filename
        self.file = file
        return self

    def from_elements(self, list: list) -> "Document":
        """Build a document from preconstructed elements."""
        from ..tools import SettingsPreamble, Settings, Global

        self.filename = str(uuid.uuid4())[0:7]
        Global.DOCUMENT_NAME = self.filename

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]
            print(self.filename)

        if not self.dir:
            dir = Settings.Export.export_dir
            self.dir = os.path.expanduser(dir[:-1] if dir.endswith("/") else dir)

        file = File(
            filename=self.filename,
            parrentdir=self.dir + "/" + self.filename.replace(".md", ""),
        )

        dir_depended_classes = [File, Quote]

        for i, el in enumerate(list):
            if isinstance(el, Document):
                raise TypeError(
                    "Can't pass Document to Document.from_elements() function"
                )
            if type(el) in dir_depended_classes:
                if not list[i].parrentdir:
                    list[i].parrentdir += "/" + self.filename.replace(".md", "")
                list[i].filedepth += 1

        file.from_elements(list)
        # file.filename = self.filename
        self.file = file

        return self

    def _process_settings_logics(self) -> None:
        pass

    def check(self) -> None:
        """Print contained file diagnostics and reset global state."""
        from ..tools import SettingsPreamble, Settings, Global

        if self.file:
            self.file.check()
        else:
            print("Document is not initialized")

        Global.check()
        Global.to_default()

    def to_latex(self) -> str:
        """Render the document to a full LaTeX string with preamble and body."""
        from ..tools import SettingsPreamble, Settings, Global

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
        """Write the rendered LaTeX document to a file.

        Args:
            filename: Optional override for output filename; defaults to derived from markdown name.

        Returns:
            None

        Side Effects:
            Writes LaTeX files to disk and may create makefiles.
        """
        from ..tools import SettingsPreamble, Settings, Global

        file = self.to_latex()

        if not filename:
            filename = self.filename.replace(".md", "") + ".tex"

        # with open(os.getcwd() + "/" + filename, "w") as f:
        os.makedirs(self.dir, exist_ok=True)

        with open(os.path.join(self.dir, filename), "w") as f:
            f.write(file)

        if Settings.Export.makefile:
            Makefile.to_file(self.dir)

        Global.to_default()

    def to_latex_project(self, filename="") -> None:
        """Create a full LaTeX project directory with includes and assets.

        Args:
            filename: Optional override for main filename.

        Returns:
            None

        Raises:
            ValueError: If the document or file is not initialized before export.

        Side Effects:
            Writes multiple files/directories and copies theme assets when needed.
        """
        from ..tools import SettingsPreamble, Settings, Global
        # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename

        if not self.filename or not self.file:
            raise ValueError("Document must be initialized")

        if self.file:
            main = self.file
        else:
            raise ValueError("Document is not initialized")

        try:
            os.makedirs(self.dir + "/" + self.filename.replace(".md", ""))
        except:
            # print("Не удалось создать директорию проекта или она уже создана")
            pass

        main = main._to_latex_project()

        if Settings.Export.makefile:
            Makefile.to_file(self.dir + "/" + self.filename.replace(".md", ""))

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
            os.path.join(self.dir, self.filename.replace(".md", ""), "main.tex"), "w"
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
                copy_dir = os.path.join(self.dir, self.filename.replace(".md", ""))

                shutil.copy2(style_dir, copy_dir)
            else:
                print(f"{SettingsPreamble.Beamer.theme} not found in JSON file")

        Global.to_default()
