from PIL import Image as PillowImage

from tools.search import find_file


class Image:
    def _get_image_dimensions(self):
        try:
            with PillowImage.open(self.dir) as img:
                return img.width, img.height
        except FileNotFoundError:
            return None, None

    def __init__(
        self,
        filename: str,
        parrentfilename: str,
        caption="",
        width=None,
        height=None,
        settings={},
    ) -> None:
        self.filename = filename
        self.parrentfilename = parrentfilename

        self.dir = find_file(filename, settings=settings["dir"])

        self.caption = caption

        self.width = width
        self.height = height
        self.original_width, self.orgigna_height = self._get_image_dimensions()

        self.reference = None

    def to_latex(self, setting={}):
        """
        Генерирует LaTeX-код для вставки изображения
        """
        # Проверяем, найдено ли изображение
        if not self.dir or not self.original_width or not self.orgigna_height:
            return f"\\colorbox{{red}}{{FILE NOT FOUND: {self.filename}}} \\newline\n"

        # Формируем метку для ссылки, если есть reference
        label_str = ""
        if self.reference:
            label_str = f"\\label{{fig:{self.reference}}}"

        # Начинаем формирование LaTeX-кода
        latex_code = []
        latex_code.append(f"\\begin{{figure}}[H]")
        latex_code.append("    \\centering")

        # Добавляем метку, если есть
        if label_str:
            latex_code.append(f"    {label_str}")

        # Определяем параметры изображения
        includegraphics_params = []

        # Если заданы и ширина, и высота
        if self.width and self.height:
            scale_width = self.width / self.original_width
            scale_height = self.height / self.orgigna_height
            includegraphics_params.append(f"width = {{{scale_width}}}\\textwidth")
            includegraphics_params.append(f"height = {{{scale_height}}}\\textheight")

        # Если задана только ширина
        elif self.width:
            scale = self.width / self.original_width
            includegraphics_params.append(f"scale = {{{scale}}}")
            includegraphics_params.append("keepaspectratio")

        # Если не заданы размеры, используем автоматическое масштабирование
        else:
            k = self.original_width / self.orgigna_height

            if k < 0.6:  # Высокое изображение
                includegraphics_params.append("height = \\textheight")
                includegraphics_params.append("keepaspectratio")
            elif k < 1.5:  # Квадратное или близкое к квадратному
                if self.original_width < self.orgigna_height:
                    includegraphics_params.append("width = 8cm")
                else:
                    includegraphics_params.append("height = 8cm")
                includegraphics_params.append("keepaspectratio")
            else:  # Широкое изображение
                includegraphics_params.append("width = \\textwidth")
                includegraphics_params.append("keepaspectratio")

        # Формируем строку с параметрами
        params_str = ", ".join(includegraphics_params)

        # Добавляем команду includegraphics
        latex_code.append(f"    \\includegraphics[{params_str}]{{{self.dir}}}")

        # Добавляем подпись, если есть
        if self.caption:
            latex_code.append(f"    \\caption{{{self.caption}}}")

        # Закрываем окружение figure
        latex_code.append("\\end{figure}")

        return "\n".join(latex_code) + "\n"

    def to_latex_project(self):
        return self.to_latex()


class ImageFrame:
    a = 1
