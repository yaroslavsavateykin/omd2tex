import shutil
from PIL import Image as PillowImage
import os

from objects import reference
from tools.search import find_file


class Image:
    def __init__(
        self,
        filename: str,
        parrentdir: str,
        caption="",
        width=None,
        height=None,
        settings={},
    ) -> None:
        self.filename = filename
        self.parrentdir = parrentdir
        self.settings = settings

        self.dir = find_file(filename, settings["dir"])

        self.caption = caption

        self.width = width
        self.height = height
        self.original_width, self.original_height = self._get_image_dimensions()

        self.reference = None

    def _identify_reference(self) -> None:
        if self.reference:
            global GLOBAL_REFERENCE_DICT

            GLOBAL_REFERENCE_DICT[self.reference] = "fig"
        else:
            GLOBAL_REFERENCE_DICT[self.reference] = "not_found_headline"

    def _get_image_dimensions(self):
        try:
            with PillowImage.open(self.dir) as img:
                return img.width, img.height
        except FileNotFoundError:
            return None, None

    def to_latex(self, setting={}):
        if self.reference:
            self.reference = f"\\label{{fig:{self.reference}}}"
        else:
            self.reference = ""

        if self.caption:
            self.caption = f"\\caption{{{self.caption}}}"
        else:
            self.caption = ""

        dir = self.dir
        settings = self.settings.get("image", {})

        if self.width:
            if self.height:
                scale_width = self.width / self.original_width
                scale_height = self.height / self.original_height

                image_include = f"\\includegraphics[width = {{{scale_width}}}\\textwidth, height = {{{scale_height}}}\\textheight]{{{dir}}}"
            else:
                scale = self.width / self.original_width
                image_include = (
                    f"\\includegraphics[scale = {{{scale}}},keepaspectratio]{{{dir}}}"
                )
        else:
            wh_ratio = self.original_width / self.original_height

            if wh_ratio < settings.get("wh_aspect_borders", [0.6, 1.8])[0]:
                image_include = f"\\includegraphics[height = \\textheight, keepaspectratio]{{{dir}}}"
            elif wh_ratio < settings.get("wh_aspect_borders", [0.6, 1.8])[1]:
                if self.original_width < self.original_height:
                    image_include = f"\\includegraphics[width = {settings.get('default_width', '8cm')}, keepaspectratio]{{{dir}}}"
                else:
                    image_include = f"\\includegraphics[height = {settings.get('default_height', '8cm')}, keepaspectratio]{{{dir}}}"
            else:
                image_include = (
                    f"\\includegraphics[width = \\textwidth, keepaspectratio]{{{dir}}}"
                )

        latex_lines = f"""\\begin{{figure}}[H] 
\\centering
{self.reference}
{image_include}
{self.caption}
\\end{{figure}}
"""
        return latex_lines

    def _copy_to_folder(self) -> None:
        dir = self.parrentdir + "/images/"
        try:
            os.makedirs(dir)
        except:
            pass

        shutil.copy2(self.dir, dir)

    def _ralative_paths(self) -> None:
        self.parrentdir = "."
        self.dir = "."

    def to_latex_project(self):
        self._copy_to_folder()

        self._ralative_paths()

        self.dir = self.parrentdir + "/images/" + self.filename

        return self.to_latex()


class ImageFrame:
    a = 1
