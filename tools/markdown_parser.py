import re
import yaml

from tools.search import find_file
from objects.equation import Equation
from objects.paragraph import Paragraph
from objects.codeblock import CodeBlock
from objects.reference import Reference
from objects.headline import Headline
from objects.table import Table
from objects.image import Image, ImageFrame
from objects.quote import Quote
from objects.footnote import Footnote
from tools.settings import Settings


class MarkdownParser:
    re_table_row = re.compile(r"^\|(.+)\|$")
    re_image = re.compile(r"^!\[(.*?)\]\((.*?)\)")
    re_link = re.compile(r"^\[(.*?)\]\((.*?)\)")
    re_comment = re.compile(r"^<!--(.*?)-->$")

    re_text_files1 = re.compile(
        r"!?\[\[([^|\[\]]+?(?:\.(?:md|tex|txt))?)(?:\|([^\[\]]+))?\]\]"
    )
    re_text_files2 = re.compile(r"!?\[([^\[\]]*)\]\(([^)]*?)(?:\.(md|tex|txt))?\)")

    re_reference = re.compile(r"\^([a-zA-Z0-9_-]+)")

    re_markdown_image = re.compile(
        r"!\[([^|\]]*?)(?:\|([^|\]]*?))?\]\(([^)]+)\)(?:\s*\^([a-zA-Z0-9_-]+))?"
    )
    re_wiki_image = re.compile(
        r"!\[\[([^|\]]+?)(?:\|([^|\]]*?))?(?:\|([^|\]]*?))?\]\](?:\s*\^([a-zA-Z0-9_-]+))?"
    )

    re_heading = re.compile(r"^(#{1,6})\s+(.*)")

    re_footnote = re.compile(r"^\s*\[\^([^\]]+)\]:(.*)")

    def __init__(
        self,
        parrentdir: str = "",
        filename: str = "",
        filedepth: int = 0,
        quotedepth=0,
    ) -> None:
        self.filename = filename

        if self.filename and (
            Settings.Export.branching_project
            and not parrentdir.endswith(self.filename.strip(".md"))
        ):
            self.parrentdir = parrentdir + "/" + self.filename.strip(".md")
        else:
            self.parrentdir = parrentdir

        self.filedepth = filedepth
        self.quotedepth = quotedepth

        self.dir_filename = find_file(filename, search_path=Settings.Export.search_dir)

        self.yaml = None

    @staticmethod
    def __parse_size_parameter(size_str):
        """
        Парсит строку размера в формате "300" или "300x200"
        Возвращает (width, height) или (None, None)
        """
        if not size_str or not re.match(r"^\d+(x\d+)?$", size_str.strip()):
            return None, None

        size_parts = size_str.strip().split("x")
        width = int(size_parts[0])
        height = int(size_parts[1]) if len(size_parts) > 1 else None
        return width, height

    def parse(self, lines=[]):
        from objects.file import File

        non_md_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".svg",
            ".gif",  # Изображения
            ".docx",
            ".pdf",
            ".xlsx",
            ".pptx",  # Документы
            ".zip",
            ".tar",
            ".gz",  # Архивы
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",  # Медиа
        ]

        image_extensions = [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".svg",
        ]

        if not lines:
            with open(self.dir_filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

        i = 0
        in_yaml = False
        in_code_block = False
        in_equation = False
        in_table = False
        in_quote = False

        elements = []

        while i < len(lines):
            line = lines[i]

            # Skipping ""
            if not line.strip():
                i += 1
                continue

            # READING YAML
            if i == 0 and line.startswith("---"):
                in_yaml = True
                yaml_lines = []
                i += 1
                continue

            if in_yaml:
                if line.startswith("---"):
                    in_yaml = False
                    if yaml_lines:
                        self.yaml = yaml.safe_load("\n".join(yaml_lines))
                    i += 1
                    continue
                else:
                    yaml_lines.append(line)
                    i += 1
                    continue

            m = self.re_footnote.match(line)
            if m:
                footnote_key, footnote_text = m.groups()
                Footnote.append(footnote_key, footnote_text)
                i += 1
                continue

            m = self.re_markdown_image.match(line)
            if m:
                alt_text, size_param, filename, ref_link = m.groups()

                if not any(filename.lower().endswith(ext) for ext in image_extensions):
                    i += 1
                    continue

                if filename.startswith("#^"):
                    i += 1
                    continue

                width, height = self.__parse_size_parameter(size_param)
                caption = alt_text if alt_text else None

                image_obj = Image(
                    filename=filename,
                    parrentdir=self.parrentdir,
                    caption=caption,
                    width=width,
                    height=height,
                )
                if ref_link:
                    image_obj.reference = ref_link

                elements.append(image_obj)
                i += 1
                continue

            n = self.re_wiki_image.match(line)
            if n:
                filename, param1, param2, ref_link = n.groups()

                if not any(filename.lower().endswith(ext) for ext in image_extensions):
                    i += 1
                    continue

                if filename.startswith("#^"):
                    i += 1
                    continue

                width = None
                height = None
                caption = None
                reference = None

                if param2:
                    width, height = self.__parse_size_parameter(param2)
                    if width is not None:
                        reference = param1 if param1 else None
                    else:
                        width, height = self.__parse_size_parameter(param1)
                        if width is None:
                            reference = param1 if param1 else None
                            caption = param2 if param2 else None
                        else:
                            caption = param2 if param2 else None
                else:
                    if param1:
                        width, height = self.__parse_size_parameter(param1)
                        if width is None:
                            reference = param1

                image_obj = Image(
                    filename=filename,
                    parrentdir=self.parrentdir,
                    caption=caption,
                    width=width,
                    height=height,
                )

                if reference:
                    image_obj.reference = reference

                if ref_link:
                    image_obj.reference = ref_link

                elements.append(image_obj)
                i += 1
                continue

            # Extracting text files
            m = self.re_text_files1.match(line)
            if m:
                if self.filedepth >= Settings.File.max_file_recursion:
                    raise RecursionError(
                        f"Maximum file nesting filedepth ({Settings.File.max_file_recursion}) exceeded"
                    )
                filename, _ = m.groups()

                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    i += 1
                    continue

                if any(filename.endswith(ext) for ext in non_md_extensions):
                    i += 1
                    continue

                if filename.startswith("#^"):
                    i += 1
                    continue

                elements.append(
                    File(
                        filename=filename + ".md"
                        if not filename.endswith(".md")
                        else filename,
                        parrentfilename=self.filename,
                        parrentdir=self.parrentdir,
                        filedepth=self.filedepth + 1,
                    )
                )
                i += 1
                continue

            n = self.re_text_files2.match(line)
            if n:
                if self.filedepth >= Settings.File.max_file_recursion:
                    raise RecursionError(
                        f"Maximum file nesting filedepth ({Settings.File.max_file_recursion}) exceeded"
                    )
                _, filename, extension = n.groups()
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    i += 1
                    continue

                if filename.startswith("#^"):
                    i += 1
                    continue
                if any(filename.endswith(ext) for ext in non_md_extensions):
                    i += 1
                    continue

                if extension:
                    full_filename = f"{filename}.{extension}"
                else:
                    full_filename = (
                        filename + ".md" if not filename.endswith(".md") else filename
                    )

                elements.append(
                    File(
                        full_filename,
                        parrentfilename=self.filename,
                        parrentdir=self.parrentdir,
                        filedepth=self.filedepth + 1,
                    )
                )
                i += 1
                continue

            # БЛОКИ КОДА
            if line.startswith("```") and not in_code_block:
                blocktype = line.strip("```").strip()
                blocklines = []
                in_code_block = True
                i += 1
                continue

            if in_code_block:
                if line.startswith("```"):
                    if blocklines:
                        elements.append(
                            CodeBlock(
                                blocktype,
                                blocklines,
                            )
                        )
                    in_code_block = False
                    i += 1
                    continue
                else:
                    blocklines.append(line)
                    i += 1
                    continue

            # Переделываем ссылки на другие элементы
            m = self.re_reference.match(line)
            if m:
                elements.append(Reference(m.group()[1:]))

                i += 1
                continue

            # УРАВНЕНИЯ
            if line.strip().startswith("$$") or line.strip().endswith("$$"):
                if not in_equation:
                    equationlines = [line.strip("$$")]
                    in_equation = True
                else:
                    if equationlines:
                        elements.append(Equation("\n".join(equationlines)))
                    in_equation = False
                i += 1
                continue

            if in_equation:
                equationlines.append(line)
                i += 1
                continue

            # Проверяем, есть ли следующая строка и начинается ли она с "|"
            next_is_table = i + 1 < len(lines) and lines[i + 1].strip().startswith("|")

            if line.strip().startswith("|"):
                if not in_table:
                    in_table = True
                    tablelines = [line]
                else:
                    tablelines.append(line)

                # Если текущая строка последняя ИЛИ следующая строка НЕ таблица
                if i == len(lines) - 1 or not next_is_table:
                    if len(tablelines) >= 2:  # Проверяем минимальный формат
                        elements.append(Table(tablelines))
                        in_table = False
                        tablelines = []
                i += 1
                continue

            else:
                if in_table:
                    if len(tablelines) >= 2:
                        elements.append(Table(tablelines))
                    in_table = False
                    tablelines = []
                    i += 1
                    continue

            # Проверяем, есть ли следующая строка и начинается ли она с ">"
            next_is_quote = i + 1 < len(lines) and lines[i + 1].strip().startswith(">")

            if line.strip().startswith(">"):
                if not in_quote:
                    in_quote = True
                    quotelines = [line]
                else:
                    quotelines.append(line)

                # Если текущая строка последняя ИЛИ следующая строка НЕ цитата
                if i == len(lines) - 1 or not next_is_quote:
                    if self.quotedepth >= Settings.Quote.max_quote_recursion:
                        raise RecursionError(
                            f"Maximum quote nesting quotedepth ({Settings.Quote.max_quote_recursion}) exceeded"
                        )
                    elements.append(
                        Quote(
                            quotelines=quotelines,
                            filename=self.filename,
                            parrentfilename=self.filename,
                            parrentdir=self.parrentdir,
                            quotedepth=self.quotedepth + 1,
                        )
                    )
                    in_quote = False
                    quotelines = []
                i += 1
                continue

            else:
                if in_quote:
                    if self.quotedepth >= Settings.Quote.max_quote_recursion:
                        raise RecursionError(
                            f"Maximum quote nesting quotedepth ({Settings.Quote.max_quote_recursion}) exceeded"
                        )
                    elements.append(
                        Quote(
                            quotelines=quotelines,
                            filename=self.filename,
                            parrentfilename=self.filename,
                            parrentdir=self.parrentdir,
                            quotedepth=self.quotedepth + 1,
                        )
                    )
                    in_quote = False
                    quotelines = []
                    i += 1
                    continue

                # ЗАГОЛОВКИ
            n = self.re_heading.match(line)
            if n:
                level, line = n.groups()
                elements.append(Headline(len(level) - 1, line))
                i += 1
                continue

            # Параграф
            paragraph_lines = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].strip().startswith(">")
            ):
                paragraph_lines.append(lines[i])
                i += 1
            joined = "\n".join(line.strip() for line in paragraph_lines)
            elements.append(Paragraph(joined))

        Footnote.to_default()

        return elements
