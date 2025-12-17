import shutil
from PIL import Image as PillowImage
import os

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
        caption="",
        width=None,
        height=None,
        dir=None,
    ) -> None:
        super().__init__()
        self.filename = filename
        self.parrentdir = parrentdir

        if dir is None:
            self.dir = find_file(filename, Settings.Export.search_dir)
        else:
            self.dir = dir

        self.caption = caption

        self.width = width
        self.height = height
        self.original_width, self.original_height = self._get_image_dimensions()

        self.reference = None

    def _identify_reference(self) -> None:
        if self.reference:
            Global.REFERENCE_DICT[self.reference] = "fig"
        else:
            Global.REFERENCE_DICT[self.reference] = "not_found_fig"

    def _get_image_dimensions(self):
        try:
            with PillowImage.open(self.dir) as img:
                return img.width, img.height
        except FileNotFoundError:
            return None, None

    def to_latex(self):
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
            image_include = f"\\adjustbox{{max width=\\textwidth, max height=\\textheight, keepaspectratio}}{{\\includegraphics[height = \\textheight/(3/2), keepaspectratio]{{{dir}}}}}"
        else:
            if self.width:
                if self.height:
                    scale_width = self.width / self.original_width
                    scale_height = self.height / self.original_height

                    image_include = f"\\includegraphics[width = {{{scale_width}}}\\textwidth, height = {{{scale_height}}}\\textheight]{{{dir}}}"
                else:
                    scale = self.width / self.original_width
                    image_include = f"\\includegraphics[scale = {{{scale}}},keepaspectratio]{{{dir}}}"
            else:
                wh_ratio = self.original_width / self.original_height

                if wh_ratio < Settings.Image.wh_aspect_borders[0]:
                    image_include = f"\\includegraphics[height = \\textheight, keepaspectratio]{{{dir}}}"
                elif wh_ratio < Settings.Image.wh_aspect_borders[1]:
                    if self.original_width < self.original_height:
                        image_include = f"\\includegraphics[width = {Settings.Image.default_width}, keepaspectratio]{{{dir}}}"
                    else:
                        image_include = f"\\includegraphics[height = {Settings.Image.default_height}, keepaspectratio]{{{dir}}}"
                else:
                    image_include = f"\\includegraphics[width = \\textwidth, keepaspectratio]{{{dir}}}"

        latex_lines = f"""\\begin{{figure}}[H] 
\\centering
{image_include}
{caption}
{reference}
\\end{{figure}}"""

        return latex_lines

    def _copy_to_folder(self) -> None:
        dir_path = os.path.join(self.parrentdir, "images")
        os.makedirs(dir_path, exist_ok=True)

        filename = os.path.basename(self.dir)
        destination = os.path.join(dir_path, filename)

        if os.path.exists(destination):
            os.remove(destination)

        if os.path.isfile(self.dir):
            shutil.copy2(self.dir, destination)
        else:
            raise FileNotFoundError(f"Файл {self.dir} не найден")

    def _relative_paths(self) -> None:
        self.parrentdir = "."
        self.dir = "."

    def _to_latex_project(self):
        if not Settings.Image.absolute_path_in_project_export:
            self._relative_paths()

            self.dir = os.path.join(self.parrentdir, "images", self.filename)

        if Settings.Image.copy_to_folder_in_project_export:
            self._copy_to_folder()

        return self.to_latex()


class ImageFrame:
    a = 1
