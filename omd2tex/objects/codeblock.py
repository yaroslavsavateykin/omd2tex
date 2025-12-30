from ..tools.settings import Settings
from ..tools.globals import Global
from .image import Image
from .base import BaseClass
from .fragment import Caption
from .paragraph import Paragraph


class CodeBlock(BaseClass):
    def __init__(self, blocktype: str, blocklines: list) -> None:
        """Initialize a code block wrapper with type and lines."""

        super().__init__()
        self.blocktype = blocktype
        self.blocklines = blocklines
        self.reference = None
        self.caption = None

    @staticmethod
    def _minted_python(blocklines: list) -> Paragraph:
        """Render a Python code block using minted."""

        joined_lines = "\n".join(blocklines)
        block = (
            "\\usemintedstyle{default}\n"
            "\\begin{minted}[mathescape, linenos, numbersep=5pt, frame=lines, framesep=2mm, breaklines]{python} \n"
            f"{joined_lines}\n"
            "\\end{minted}"
        )

        return Paragraph(block, parse=False)

    @staticmethod
    def _default_codeblock(blocklines: list) -> Paragraph:
        """Render a generic code block using tcolorbox and verbatim."""
        joined_lines = "\n".join(blocklines)
        block = (
            "\\begin{tcolorbox}[colback=gray!20, colframe=gray!50, sharp corners, boxrule=1pt]\n"
            "\\begin{verbatim}\n"
            f"{joined_lines}\n"
            "\\end{verbatim}\n"
            "\\end{tcolorbox}"
        )

        return Paragraph(block, parse=False)

    @staticmethod
    def _create_picture_from_smiles(lines: list):
        """Create an image from SMILES strings or reactions using RDKit."""
        from rdkit import Chem
        from rdkit.Chem import Draw
        from rdkit.Chem.Draw import IPythonConsole
        from rdkit.Chem import rdChemReactions
        from PIL import Image as PILImage, ImageDraw, ImageFont
        import uuid
        import os

        font_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../default/fonts/cmunrm.ttf"
        )
        IPythonConsole.drawOptions.fontFile = font_path

        from PIL import Image as PILImage, ImageDraw, ImageFont

        def _add_conditions_banner(
            img: PILImage.Image, text: str, font_path: str
        ) -> PILImage.Image:
            """
            Добавляет над картинкой реакций белую полоску с текстом условий.
            Работает и с новой Pillow (без textsize), и со старой.
            """
            if not text:
                return img

            # Подбираем шрифт
            try:
                base_size = max(10, int(img.height * 0.08))
                font = ImageFont.truetype(font_path, size=base_size)
            except Exception:
                font = ImageFont.load_default()

            # --- считаем размер текста ---
            try:
                # Новый способ (Pillow 9+/10+): через bounding box шрифта
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                # Старые версии Pillow: fallback через textsize
                dummy = PILImage.new("RGB", (1, 1), "white")
                draw_dummy = ImageDraw.Draw(dummy)
                text_width, text_height = draw_dummy.textsize(text, font=font)

            padding_x = 10
            padding_y = 6
            banner_height = text_height + 2 * padding_y

            W, H = img.size
            new_W = W
            new_H = H + banner_height

            # Новая картинка: сверху баннер, снизу исходная реакция
            new_img = PILImage.new("RGB", (new_W, new_H), "white")
            new_img.paste(img, (0, banner_height))

            draw = ImageDraw.Draw(new_img)
            text_x = max(padding_x, (new_W - text_width) // 2)
            text_y = (banner_height - text_height) // 2

            draw.text((text_x, text_y), text, font=font, fill="black")

            return new_img

        raw_lines = [s.strip() for s in lines if s.strip()]
        if not raw_lines:
            return Paragraph("")

        parsed = []
        for s in raw_lines:
            smi_part = s
            cond = None
            if "#" in s:
                smi_part, cond = s.split("#", 1)
                smi_part = smi_part.strip()
                cond = cond.strip()
            parsed.append((smi_part, cond))

        smiles_only = [p[0] for p in parsed]

        # реакция или отдельные молекулы
        is_reaction = all((">>" in s or "<<" in s) for s in smiles_only)

        # === РЕАКЦИЯ ===
        if is_reaction:
            rxn_smi, conditions = parsed[0]

            rxn = rdChemReactions.ReactionFromSmarts(rxn_smi, useSmiles=True)
            if rxn is None:
                return Paragraph("")

            pic = Draw.ReactionToImage(rxn, subImgSize=(500, 300))

            if conditions:
                pic = _add_conditions_banner(pic, conditions, font_path)

            molsPerRow = 1  # просто маркер, что одна картинка

        # === МОЛЕКУЛЫ ===
        else:
            mols = []
            for smi, _ in parsed:
                m = Chem.MolFromSmiles(smi)
                if m is not None:
                    mols.append(m)

            if not mols:
                return Paragraph("")

            mols_num = len(mols)
            molsPerRow = 2 if mols_num > 2 else mols_num

            pic = Draw.MolsToGridImage(
                mols, returnPNG=False, subImgSize=(500, 300), molsPerRow=molsPerRow
            )

        # --- сохранение результата ---
        unique_filename = str(uuid.uuid4()) + ".png"

        export_dir = os.path.expanduser(
            os.path.join(
                Settings.Export.export_dir, Global.DOCUMENT_NAME.replace(".md", "")
            )
        )
        pic_abs_path = os.path.expanduser(
            os.path.join(export_dir, "images", unique_filename)
        )

        images_path = os.path.join(export_dir, "images")

        try:
            os.makedirs(images_path, exist_ok=True)
            print(f"Директория создана: {images_path}")
        except PermissionError:
            print(f"Ошибка: нет прав для создания {images_path}")
        except OSError as e:
            print(f"Ошибка при создании директории: {e}")

        pic.save(pic_abs_path)

        # ВАЖНОЕ ИЗМЕНЕНИЕ:
        # - одна молекула -> width=100 (уменьшаем)
        # - реакция -> полный размер (width не задаём)
        if molsPerRow == 1 and not is_reaction:
            image = Image(
                filename=unique_filename,
                parrentdir=export_dir,
                dir=pic_abs_path,
                width=100,
            )
        else:
            # реакции (is_reaction=True) и сетка молекул -> оригинальный размер
            image = Image(
                filename=unique_filename,
                parrentdir=export_dir,
                dir=pic_abs_path,
            )

        return image

    @staticmethod
    def _add_preamble_commands(lines: list):
        Global.NEW_COMMANDS_PREAMBLE.append("\n".join(lines))

        return Paragraph("")

    def _apply_blocktype(self) -> BaseClass:
        """Dispatch block rendering based on the specified block type."""
        functions = {
            "example": lambda content: Paragraph(
                "\\begin{example}\n" + "\n".join(content) + "\n\\end{example}"
            ),
            "hidden": lambda content: Paragraph("", parse=False),
            "text": lambda content: Paragraph("\n".join(content)),
            "caption": lambda content: Caption(" ".join(content)),
            "pause": lambda content: Paragraph("\\pause", parse=False),
            "python": self._minted_python,
            "c": self._minted_python,
            "cpp": self._minted_python,
            "c++": self._minted_python,
            "java": self._minted_python,
            "bash": self._minted_python,
            "smiles": self._create_picture_from_smiles,
            "preamble": self._add_preamble_commands,
        }
        if self.blocktype in functions:
            return functions[self.blocktype](self.blocklines)
        else:
            return self._default_codeblock(self.blocklines)

    @classmethod
    def create(cls, blocktype: str, blocklines: list) -> BaseClass:
        """Factory method to create and render a code block element."""
        instance = cls.__new__(cls)
        instance.blocktype = blocktype
        instance.blocklines = blocklines
        instance.reference = None
        return instance._apply_blocktype()

    def to_latex(self) -> str:
        """Render the code block to LaTeX."""
        return self._apply_blocktype().to_latex()

    def _to_latex_project(self) -> str:
        return self.to_latex()
