import json
import os
import shutil
import copy
from pathlib import Path
from typing import Any, Dict, Union
import uuid

from .base import BaseClass

from .citation import Citation
from .makefile import Makefile
from .paragraph import Paragraph
from .preamble import Preamble
from .file import File
from .quote import Quote
from ..tools.path_utils import (
    export_project_name,
    normalize_export_dir,
    package_default_dir,
    stem_md,
)
from ..tools.config_base import ConfigBase


def _snapshot_config(config_class):
    snapshot = {}
    for name, value in vars(config_class).items():
        if name.startswith("_"):
            continue
        if isinstance(value, type) and issubclass(value, ConfigBase):
            snapshot[name] = _snapshot_config(value)
        elif not callable(value):
            snapshot[name] = copy.deepcopy(value)
    return snapshot


def _restore_config(config_class, snapshot) -> None:
    for name, value in snapshot.items():
        current = getattr(config_class, name)
        if isinstance(value, dict) and isinstance(current, type) and issubclass(
            current, ConfigBase
        ):
            _restore_config(current, value)
        else:
            setattr(config_class, name, copy.deepcopy(value))


class Document(BaseClass):
    def __init__(
        self,
        filename: str = "",
        settings: Union[Dict[str, Any], str] = None,
        preamble: str = None,
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
        # A new document must not inherit references or citations from a prior one.
        Global.to_default()
        if settings:
            Settings.update(settings)
        if preamble:
            Settings.Preamble.settings_json = preamble

        self._base_settings = _snapshot_config(Settings)
        self._base_preamble_settings = _snapshot_config(SettingsPreamble)
        self._render_settings = self._base_settings
        self._render_preamble_settings = self._base_preamble_settings

        self.dir = normalize_export_dir(Settings.Export.export_dir)

        self.filename = filename
        self.file = None

        if Settings.Preamble.create_preamble:
            self.preamble = Preamble()

        else:
            self.preamble = Paragraph("")

        export = os.path.expanduser(Settings.Export.export_dir)
        search = os.path.expanduser(Settings.Export.search_dir)
        export_rel = os.path.relpath(export, search)
        if export_rel not in Settings.Export.search_ignore_dirs:
            Settings.Export.search_ignore_dirs.append(export_rel)

    def from_file(self, filename: str) -> "Document":
        """Load and parse a markdown file into a Document."""
        from ..tools import SettingsPreamble, Settings, Global

        self.filename = filename
        Global.DOCUMENT_NAME = export_project_name(self.filename)
        project_subdir = str(Path(self.dir) / export_project_name(self.filename))
        file = File(
            filename=self.filename,
            parrentdir=project_subdir,
        )
        file.from_file(filename)
        self.file = file
        self._remember_render_settings()
        return self

    def from_text(self, text: str, source_dir: str = None) -> "Document":
        """Create a document from raw markdown text."""
        from ..tools import SettingsPreamble, Settings, Global

        self.filename = str(uuid.uuid4())[0:7]
        Global.DOCUMENT_NAME = self.filename
        project_subdir = str(Path(self.dir) / stem_md(self.filename))
        file = File(
            filename=self.filename,
            parrentdir=project_subdir,
        )
        file.from_text(text, source_dir=source_dir)
        # file.filename = self.filename
        self.file = file
        self._remember_render_settings()
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
            self.dir = normalize_export_dir(dir)

        project_subdir = str(Path(self.dir) / stem_md(self.filename))
        file = File(
            filename=self.filename,
            parrentdir=project_subdir,
        )

        dir_depended_classes = [File, Quote]

        for i, el in enumerate(list):
            if isinstance(el, Document):
                raise TypeError(
                    "Can't pass Document to Document.from_elements() function"
                )
            if type(el) in dir_depended_classes:
                if not list[i].parrentdir:
                    list[i].parrentdir = self.dir
                list[i].filedepth += 1

        file.from_elements(list)
        # file.filename = self.filename
        self.file = file
        self._remember_render_settings()

        return self

    def _remember_render_settings(self) -> None:
        from ..tools import Settings, SettingsPreamble

        self._render_settings = _snapshot_config(Settings)
        self._render_preamble_settings = _snapshot_config(SettingsPreamble)

    def _restore_render_settings(self) -> None:
        from ..tools import Settings, SettingsPreamble

        _restore_config(Settings, self._render_settings)
        _restore_config(SettingsPreamble, self._render_preamble_settings)

    def _restore_base_settings(self) -> None:
        from ..tools import Settings, SettingsPreamble

        _restore_config(Settings, self._base_settings)
        _restore_config(SettingsPreamble, self._base_preamble_settings)

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

        if not self.file:
            raise ValueError("Document must be initialized")

        self._restore_render_settings()
        try:
            preamble = self.preamble.to_latex()

            # НЕЛЬЗЯ ПЕРЕДАВАТЬ parrentfilename
            file = self.file.to_latex()

            if Global.CITATION_INITIALIZED:
                citations = Citation.to_latex_preamble()
                bibliography = "\\newpage\\printbibliography"
            else:
                citations = ""
                bibliography = ""

            beamer_titlepage = getattr(self.preamble, "beamer_titlepage", False)

            document = rf"""
{preamble}

{citations}

\begin{{document}}
{"\\frame{\\titlepage}" if beamer_titlepage and self.preamble else ""}

{file}

{bibliography}

\end{{document}}"""

            return document
        finally:
            self._restore_base_settings()

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
            filename = export_project_name(self.filename) + ".tex"
        else:
            filename = Path(filename).name
            if filename in {"", ".", ".."}:
                raise ValueError("Output filename must be a file name")

        # with open(os.getcwd() + "/" + filename, "w") as f:
        os.makedirs(self.dir, exist_ok=True)

        with open(os.path.join(self.dir, filename), "w") as f:
            f.write(file)

        if Settings.Export.makefile:
            Makefile.to_file(self.dir)


    def to_latex_project(self) -> None:
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

        # if save_dir:
        #     self.dir = save_dir
        #     self.file.parrentdir = save_dir

        if not self.filename or not self.file:
            raise ValueError("Document must be initialized")

        self._restore_render_settings()

        if self.file:
            main = self.file
        else:
            raise ValueError("Document is not initialized")

        try:
            os.makedirs(str(Path(self.dir) / export_project_name(self.filename)))
        except:
            # print("Не удалось создать директорию проекта или она уже создана")
            pass

        main = main._to_latex_project()

        if Settings.Export.makefile:
            Makefile.to_file(str(Path(self.dir) / export_project_name(self.filename)))

        if Global.CITATION_INITIALIZED:
            citations = Citation.to_latex_preamble()
            bibliography = "\\newpage\\printbibliography"
        else:
            citations = ""
            bibliography = ""

        beamer_titlepage = getattr(self.preamble, "beamer_titlepage", False)

        document = f"""
{self.preamble._to_latex_project()}

{citations}

\\begin{{document}}
{"\\frame{\\titlepage}" if beamer_titlepage and self.preamble else ""}

{main}

{bibliography}

\\end{{document}}"""

        with open(
            str(Path(self.dir) / export_project_name(self.filename) / "main.tex"), "w"
        ) as f:
            f.write(document)

        if SettingsPreamble.documentclass == "beamer":
            style_json = str(package_default_dir() / "beamer-themes.json")
            with open(style_json, "r") as f:
                style_dict = json.loads(f.read())
            if SettingsPreamble.Beamer.theme in style_dict:
                style_dir = str(
                    package_default_dir()
                    / "beamer-themes"
                    / style_dict[SettingsPreamble.Beamer.theme]
                )
                copy_dir = str(Path(self.dir) / export_project_name(self.filename))

                shutil.copy2(style_dir, copy_dir)
            else:
                print(f"{SettingsPreamble.Beamer.theme} not found in JSON file")

        self._restore_base_settings()
