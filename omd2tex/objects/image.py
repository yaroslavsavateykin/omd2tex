import shutil
from PIL import Image as PillowImage
import os
from pathlib import Path
from typing import Optional, Tuple

from .base import BaseClass
from omd2tex.tools.settings_preamble import SettingsPreamble

from .paragraph import Paragraph
from ..tools import find_file
from ..tools import Global
from ..tools import Settings


class Image(BaseClass):
    def __init__(
        self,
        filename: str,
        parrentdir: str,
        caption: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        dir: Optional[str] = None,
    ) -> None:
        """Initialize an image element with sizing and caption metadata.

        Args:
            filename: Image filename to locate or copy.
            parrentdir: Parent directory for relative placement during export.
            caption: Optional caption text for the figure.
            width: Optional desired width in pixels.
            height: Optional desired height in pixels.
            dir: Optional explicit absolute path to the image file.

        Returns:
            None
        """
        super().__init__()
        self.filename = filename
        self.parrentdir = parrentdir

        if dir is None:
            self.dir = find_file(filename, Settings.Export.search_dir)
        else:
            self.dir = dir
        self.source_dir = self.dir

        self.caption = caption

        self.width = width
        self.height = height
        self.original_width, self.original_height = self._get_image_dimensions()

        self.reference = None

    def _identify_reference(self) -> None:
        """Register the image reference in the global reference dictionary."""
        if self.reference:
            Global.REFERENCE_DICT[self.reference] = "fig"
        else:
            Global.REFERENCE_DICT[self.reference] = "not_found_fig"

    def _get_image_dimensions(self) -> Tuple[Optional[int], Optional[int]]:
        """Return the intrinsic width and height of the image if available."""
        try:
            with PillowImage.open(self.dir) as img:
                return img.width, img.height
        except FileNotFoundError:
            return None, None

    def to_latex(self) -> str:
        """Render the image as a LaTeX figure block respecting settings."""
        if self.caption:
            caption = f"\\caption{{{Paragraph(self.caption).to_latex()}}}"
        else:
            caption = ""

        if self.reference:
            reference = f"\\label{{fig:{self.reference}}}"
            if not self.caption:
                caption = ""
        else:
            reference = ""

        dir = self.dir

        if SettingsPreamble.documentclass == "beamer":
            image_include = "\\adjustbox{max width=\\textwidth, max height=\\textheight, keepaspectratio}{\\includegraphics[height = \\textheight/(3/2), keepaspectratio]"

            latex_lines = f"\\begin{{figure}}[H]\n\\centering\n{image_include}{{{dir}}}}}\n{caption}\n{reference}\n\\end{{figure}}"

            return latex_lines

        else:
            if self.width:
                if self.height:
                    scale_width = self.width / self.original_width
                    scale_height = self.height / self.original_height

                    # print(self.width, self.height)
                    # print(self.original_width, self.original_height)
                    # print(scale_width, scale_height)
                    image_include = f"\\includegraphics[width = {{{scale_width}}}\\textwidth, height = {{{scale_height}}}\\textheight]"
                else:
                    scale = self.width / self.original_width
                    image_include = (
                        f"\\includegraphics[scale = {{{scale}}},keepaspectratio]"
                    )
            else:
                wh_ratio = self.original_width / self.original_height

                if wh_ratio < Settings.Image.wh_aspect_borders[0]:
                    image_include = (
                        f"\\includegraphics[height = \\textheight, keepaspectratio]"
                    )
                elif wh_ratio < Settings.Image.wh_aspect_borders[1]:
                    if self.original_width < self.original_height:
                        image_include = f"\\includegraphics[width = {Settings.Image.default_width}, keepaspectratio]"
                    else:
                        image_include = f"\\includegraphics[height = {Settings.Image.default_height}, keepaspectratio]"
                else:
                    image_include = (
                        f"\\includegraphics[width = \\textwidth, keepaspectratio]"
                    )

        latex_lines = f"""\\begin{{figure}}[H] 
\\centering
{image_include}{{{dir}}}
{caption}
{reference}
\\end{{figure}}"""

        return latex_lines

    def _copy_to_folder(self) -> None:
        """Copy the source image into the export project images folder."""
        dir_path = Path(self.parrentdir) / "images"
        dir_path.mkdir(parents=True, exist_ok=True)

        destination = dir_path / self.filename
        source = Path(self.source_dir or self.dir)

        if destination.exists():
            destination.unlink()

        if not source.is_file():
            found = find_file(self.filename, Settings.Export.search_dir)
            if found:
                source = Path(found)

        if source.is_file():
            shutil.copy2(str(source), str(destination))
        else:
            raise FileNotFoundError(
                f"Image file not found: {source} "
                f"(searched for '{self.filename}' in '{Settings.Export.search_dir}')"
            )

    def _relative_paths(self) -> None:
        """Adjust paths to be relative for project export."""
        self.parrentdir = "."
        self.dir = "."

    def _to_latex_project(self) -> str:
        """Render the image for inclusion in a LaTeX project and manage assets.

        Returns:
            LaTeX string for the figure while ensuring relative paths and optional copying of the source file according to settings.

        Side Effects:
            May copy image files to the project directory and mutate internal path attributes.
        """
        if Settings.Image.copy_to_folder_in_project_export:
            self._copy_to_folder()
        old_dir = self.dir
        if not Settings.Image.absolute_path_in_project_export:
            self.dir = "./images/" + self.filename
        latex = self.to_latex()
        self.dir = old_dir

        return latex


class ImageFrame:
    a = 1
