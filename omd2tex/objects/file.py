import uuid
import os
from pathlib import Path
from typing import List, Optional

from .base import BaseClass

from .list import List
from ..tools import Settings
from ..tools.path_utils import export_project_name, normalize_export_dir, stem_md
from .quote import Quote


class File(BaseClass):
    def __init__(
        self,
        filename: Optional[str] = None,
        parrentdir: Optional[str] = None,
        filedepth: int = 0,
        source_dir: Optional[str] = None,
        target: Optional[str] = None,
    ) -> None:
        """Initialize a file container for parsed markdown content.

        Args:
            filename: Name of the markdown file represented.
            parrentdir: Directory where output should be written.
            filedepth: Current recursion depth for nested files.

        Returns:
            None
        """
        from ..tools import MarkdownParser

        super().__init__()
        self.filename = filename
        self.parrentdir = parrentdir
        self.filedepth = filedepth
        self.source_dir = source_dir
        self.target = target

        if filename and parrentdir and filedepth:
            from .document import _restore_config, _snapshot_config
            from ..tools import SettingsPreamble

            settings_before = _snapshot_config(Settings)
            preamble_settings_before = _snapshot_config(SettingsPreamble)
            try:
                parser = MarkdownParser(
                    filename=filename,
                    parrentdir=parrentdir,
                    filedepth=filedepth,
                    source_dir=source_dir,
                ).from_file(filename)
                self.elements = parser.elements
                self.parrentdir = parser.parrentdir
                if target:
                    self.elements = self._select_target(self.elements, target)
            finally:
                _restore_config(Settings, settings_before)
                _restore_config(SettingsPreamble, preamble_settings_before)
        else:
            self.elements = []

    @staticmethod
    def _select_target(elements: list, target: str) -> list:
        """Select an embedded Obsidian heading or block target."""
        from .headline import Headline

        if target.startswith("^"):
            block_id = target[1:]
            return [
                element
                for element in elements
                if getattr(element, "reference", None) == block_id
            ]

        normalized = target.strip().lower()
        for index, element in enumerate(elements):
            if isinstance(element, Headline) and element.text.strip().lower() == normalized:
                selected = [element]
                for following in elements[index + 1 :]:
                    if isinstance(following, Headline) and following.level <= element.level:
                        break
                    selected.append(following)
                return selected
        return []

    def from_file(self, filename: str) -> "File":
        """Parse markdown from disk into this File instance."""
        from ..tools import MarkdownParser

        if not self.parrentdir:
            self.parrentdir = normalize_export_dir(Settings.Export.export_dir)

        parser = MarkdownParser(
            filename=filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
            source_dir=self.source_dir,
        )
        parser = parser.from_file(filename)
        self.elements = parser.elements
        # self.elements = parser.process_elements_list()

        return self

    def from_elements(self, list: List) -> "File":
        """Populate this file from an existing list of elements."""
        from ..tools import MarkdownParser
        from .document import Document

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]

        if not self.parrentdir:
            self.parrentdir = normalize_export_dir(Settings.Export.export_dir)

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
                if list[i].parrentdir:
                    list[i].parrentdir = str(
                        Path(list[i].parrentdir) / stem_md(self.filename)
                    )
                else:
                    list[i].parrentdir = str(
                        Path(self.parrentdir) / stem_md(self.filename)
                    )
                list[i].filedepth += 1
                # print(list[i].parrentdir)

        parser = parser.from_elements(list)
        # print(list)
        self.elements = parser.elements
        # self.elements = parser.process_elements_list()
        # print(self.elements)

        return self

    def from_text(self, text: str, source_dir: Optional[str] = None) -> "File":
        """Parse markdown text directly into this File instance."""
        from ..tools import MarkdownParser

        if not self.filename:
            self.filename = str(uuid.uuid4())[:7]

        if not self.parrentdir:
            self.parrentdir = normalize_export_dir(Settings.Export.export_dir)

        parser = MarkdownParser(
            filename=self.filename,
            parrentdir=self.parrentdir,
            filedepth=self.filedepth,
            source_dir=source_dir,
        )
        parser = parser.from_text(text)
        self.elements = parser.elements
        # self.elements = parser.process_elements_list()

        return self

    def check(self):
        """Print parsed elements and their LaTeX output for debugging."""
        elements = self.elements
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    def to_latex(self):
        """Render contained elements to a combined LaTeX string."""
        text = "\n\n".join([elem.to_latex() for elem in self.elements])

        return text

    def _to_latex_project(self) -> str:
        """Render contained elements for project export and write to disk.

        Returns:
            LaTeX input string referencing the generated file; may include page breaks depending on settings.

        Side Effects:
            Writes TeX files into the parent directory and adjusts paths for nested exports.
        """
        # print(self.elements)
        text = "\n\n".join([elem._to_latex_project() for elem in self.elements])

        if self.filename:
            normalized = str(self.filename).replace("\\", "/")
            if Path(normalized).is_absolute():
                filename_tex = export_project_name(normalized) + ".tex"
            else:
                filename_tex = stem_md(normalized).replace("/", "__") + ".tex"
        else:
            filename_tex = "main.tex"

        Path(self.parrentdir).mkdir(parents=True, exist_ok=True)
        with open(str(Path(self.parrentdir) / filename_tex), "w") as f:
            f.write(text)

        if Settings.File.divide_with_new_page:
            return f"\\input{{\\detokenize{{{filename_tex}}}}}\\newpage"
        else:
            return f"\\input{{\\detokenize{{{filename_tex}}}}}"
