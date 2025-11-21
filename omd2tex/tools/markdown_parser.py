import re
from typing import Union
import yaml
import uuid

from omd2tex.objects.base import BaseClass


from .settings import Settings
from .search import find_file
from .globals import Global
from .settings_preamble import SettingsPreamble


class MarkdownParser(BaseClass):
    re_text_files1 = re.compile(
        r"!?\[\[([^|\[\]]+?(?:\.(?:md|tex|txt))?)(?:\|([^\[\]]+))?\]\]"
    )
    re_text_files2 = re.compile(r"!?\[([^\[\]]*)\]\(([^)]*?)(?:\.(md|tex|txt))?\)")

    re_reference = re.compile(r"\^([a-zA-Z0-9_-]+)")

    image_extensions_pattern = r"\.(?:png|jpg|jpeg|gif|bmp|svg|webp)(?=\s*|$|\|)"

    re_markdown_image = re.compile(
        r'!\[([^\]]*?)\]\(([^\)]+?)(?:\s+"([^"]*)")?\)(?:\s*\^([a-zA-Z0-9_-]+))?',
        re.IGNORECASE,
    )

    re_wiki_image = re.compile(
        r"!?\[\[([^\]\n]+?)\]\]?(?:\s*\^([a-zA-Z0-9_-]+))?", re.IGNORECASE
    )

    re_heading = re.compile(r"^(#{1,6})\s+(.*)")

    re_footnote = re.compile(r"^\s*\[\^([^\]]+)\]:(.*)")

    enumerate_pattern = r"^(\d+)[.)]\s+(.+)$"

    def __init__(
        self,
        parrentdir: str = "",
        filename: str = "",
        filedepth: int = 0,
        quotedepth=0,
    ) -> None:
        super().__init__()
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

        self.yaml = None

        self.elements = []

    def check(self):
        elements = self.elements
        if not elements:
            print("No elements found")
        for el in elements:
            print(f"\n{el}\n{el.to_latex()}")

    @staticmethod
    def __parse_size_parameter(size_str):
        """Парсит строку размера в формате '300' или '300x200'"""
        if not size_str or not re.match(r"^\d+(x\d+)?$", size_str.strip()):
            return None, None

        size_parts = size_str.strip().split("x")
        width = int(size_parts[0])
        height = int(size_parts[1]) if len(size_parts) > 1 else None

        return width, height

    def from_file(self, filename: str):
        self.dir_filename = find_file(filename, search_path=Settings.Export.search_dir)

        if not self.dir_filename:
            return self

        else:
            self.filename = filename
            with open(self.dir_filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                self.__parse(lines)
            return self

    def from_text(self, text: Union[str, list]):
        if isinstance(text, str):
            self.__parse(text.splitlines())
        else:
            self.__parse(text)

        return self

    def from_elements(self, list: list):
        from ..objects import Document

        not_pass = [Document, MarkdownParser]

        for i, el in enumerate(list):
            for nel in not_pass:
                if isinstance(el, nel):
                    raise TypeError(
                        f"Can't pass {nel} to MarkdownParser.from_elements() function"
                    )

        self.elements = self._process_elements_list(list)
        return self

    def _process_elements_list(self, elements: list) -> list:
        from ..objects import Caption, Reference, List, SplitLine
        from .globals import Global

        elements = Reference.attach_reference(elements)
        elements = Reference.identify_elements_reference(elements)
        elements = Caption.attach_caption(elements)
        if not Global.ERROR_CATCHER:
            elements = List.append_items(elements)
            elements = List.merge_items(elements)
        if (
            SettingsPreamble.documentclass == "beamer"
            and self.quotedepth < 1
            and self.filedepth < 1
        ):
            elements = SplitLine.make_beamer(elements)

        return elements

    def __parse(self, lines: list):
        from ..objects import (
            SplitLine,
            Equation,
            Paragraph,
            CodeBlock,
            Reference,
            Headline,
            Table,
            Image,
            Quote,
            Footnote,
            Enumerate,
            Bullet,
            Check,
            File,
        )

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

        i = 0
        not_file = True
        in_yaml = False
        in_code_block = False
        in_equation = False
        in_table = False
        in_quote = False

        elements = []

        footnote = Footnote()

        while i < len(lines):
            line = lines[i]

            # Skipping ""
            if not line.strip():
                i += 1
                continue

            # CHANGING FOOTNOTE KEYS
            line = footnote.change_footnote_keys(line)
            m = self.re_footnote.match(line)
            if m:
                footnote_key, footnote_text = m.groups()

                Footnote.append(footnote_key, footnote_text)
                i += 1
                continue

            # READING YAML
            if Settings.Frontmatter.parse:
                if i == 0 and line.startswith("---"):
                    in_yaml = True
                    yaml_lines = []
                    i += 1
                    continue

                if in_yaml:
                    if line.startswith("---"):
                        in_yaml = False
                        if yaml_lines:
                            yamles = yaml.safe_load("\n".join(yaml_lines))
                            Settings.update(yamles)
                            SettingsPreamble.update(yamles)
                            for key in yamles:
                                Global.YAML_DICT[key] = yamles[key]
                            self.yaml = yamles
                        i += 1
                        continue
                    else:
                        yaml_lines.append(line)
                        i += 1
                        continue

            # БЛОКИ КОДА
            if line.startswith("```") and not in_code_block:
                START = i
                blocktype = line.strip("```").strip()
                blocklines = []
                in_code_block = True
                i += 1
                continue

            if in_code_block:
                if line.startswith("```"):
                    if blocklines:
                        el = CodeBlock.create(blocktype,blocklines)
                        el._start_line = START 
                        elements.append(el)
                    in_code_block = False
                    i += 1
                    continue
                else:
                    blocklines.append(line)
                    i += 1
                    continue

            # УРАВНЕНИЯ
            if (
                line.strip().startswith("$$")
                and line.strip().endswith("$$")
                and line.strip("$$").strip()
            ):
                if line.strip().strip("\n"):
                    START = i
                    eq = Equation(line.strip().strip("$$"))
                    eq._is_initialized = False
                    eq._start_line = START

                    elements.append(eq)
                i += 1
                continue

            if line.strip().startswith("$$"):
                

                if not in_equation:
                    equationlines = [line.strip("$$")]
                    in_equation = True
                    START = i
                else:
                    if equationlines:
                        text = "\n".join(equationlines)
                        if text.strip().strip("\n"):
                            eq = Equation("\n".join(equationlines))
                            
                            eq._start_line = START
                            elements.append(eq)
                    in_equation = False
                i += 1
                continue

            if line.strip().endswith("$$") and in_equation:
                if in_equation:
                    equationlines = [line.strip("$$")]
                    in_equation = True
                    START = i
                
                    if equationlines:
                        text = "\n".join(equationlines)
                        if text.strip().strip("\n"):
                            eq = Equation("\n".join(equationlines))
                            
                            eq._start_line = START
                            elements.append(eq)
                    in_equation = False
                i += 1
                continue
                
        
            if in_equation:
                equationlines.append(line.strip("$$"))
                i += 1
                continue

            if Settings.Fragment.Splitline.parse:
                if line.strip().startswith("---"):
                    START = i
                    el = SplitLine(line.strip().strip("---").strip("\n"))
                    el._start_line = START
                    elements.append(el)
                    i += 1
                    continue


            depth = 0
            stripped_line = line
            while stripped_line.startswith("    "):
                depth += 1
                stripped_line = stripped_line[4:]

            reference = None
            reference_match = re.search(r"\^([a-zA-Z0-9]{6})$", stripped_line)
            if reference_match:
                reference = reference_match.group(1)
                stripped_line = stripped_line[: reference_match.start()].rstrip()

            enumerate_match = re.match(r"^(\d+)[.)]\s+(.+)$", stripped_line)
            if enumerate_match:
                number = int(enumerate_match.group(1))
                text = enumerate_match.group(2)
                # print(i)
                item = Enumerate(text=text, number=number, depth=depth)
                item._start_line = i
                if reference:
                    item.reference = reference
                elements.append(item)
                i += 1
                continue

            elif stripped_line.startswith("- [") and len(stripped_line) > 4:
                complete = stripped_line[3] == "x"
                text_start = stripped_line.find("] ")
                if text_start != -1:
                    text = stripped_line[text_start + 2 :]
                else:
                    text = ""
                item = Check(text=text, complete=complete, depth=depth)
                # print(i)
                item._start_line = i
                if reference:
                    item.reference = reference
                elements.append(item)
                i += 1
                continue

            elif stripped_line.startswith("- "):
                text = stripped_line[2:]
                # print(i)
                item = Bullet(text=text, depth=depth)
                item._start_line = i
                if reference:
                    item.reference = reference
                elements.append(item)
                i += 1
                continue

            if Settings.Image.parse:
                # Обновленные регулярные выражения с проверкой расширений

                # Обработка Markdown изображений
                m = self.re_markdown_image.match(line)
                if m and not_file:
                    START = i
                    alt_text, filename, title, ref_link = m.groups()

                    # Проверяем расширение файла
                    if not re.search(
                        self.image_extensions_pattern, filename, re.IGNORECASE
                    ):
                        not_file = False
                        continue

                    if filename.startswith("#^"):
                        i += 1
                        continue

                    # Парсим параметры размера из alt text или title
                    size_param = None
                    if "|" in alt_text:
                        alt_parts = alt_text.split("|", 1)
                        alt_text, size_param = alt_parts[0], alt_parts[1]
                    elif title and "x" in title:
                        size_param = title

                    width, height = self.__parse_size_parameter(size_param)
                    caption = alt_text if alt_text else None

                    image_obj = Image(
                        filename=filename.strip(),
                        parrentdir=self.parrentdir,
                        caption=caption,
                        width=width,
                        height=height,
                    )

                    image_obj._start_line = START

                    if ref_link:
                        image_obj.reference = ref_link
                    
                    elements.append(image_obj)
                    i += 1
                    continue

                # Обработка Wiki изображений (Obsidian)
                n = self.re_wiki_image.match(line)
                if n and not_file:
                    START = i
                    content, ref_link = n.groups()

                    # Разделяем содержимое на части
                    parts = content.split("|")
                    filename = parts[0]

                    # Проверяем расширение файла
                    if not re.search(
                        self.image_extensions_pattern, filename, re.IGNORECASE
                    ):
                        not_file = False
                        continue

                    if filename.startswith("#^"):
                        i += 1
                        continue

                    # Обрабатываем дополнительные параметры
                    width, height = None, None
                    caption = None
                    size_param = None

                    if len(parts) > 1:
                        # Проверяем каждый параметр
                        for param in parts[1:]:
                            # Если параметр похож на размер
                            if re.match(r"^\d+(x\d+)?$", param):
                                size_param = param
                            # Иначе считаем это подписью
                            elif caption is None:
                                caption = param

                    width, height = self.__parse_size_parameter(size_param)

                    image_obj = Image(
                        filename=filename.strip(),
                        parrentdir=self.parrentdir,
                        caption=caption,
                        width=width,
                        height=height,
                    )

                    image_obj._start_line = START
                    if ref_link:
                        image_obj.reference = ref_link

                    elements.append(image_obj)
                    i += 1
                    continue

            if Settings.File.parse:
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
                    
                    START = i
                    
                    el = File(
                            filename=filename + ".md"
                            if not filename.endswith(".md")
                            else filename,
                            parrentdir=self.parrentdir,
                            filedepth=self.filedepth + 1,
                        )

                    el._start_line = START

                    elements.append(
                        el
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
                            filename + ".md"
                            if not filename.endswith(".md")
                            else filename
                        )
                    
                    el = File(
                            full_filename,
                            parrentdir=self.parrentdir,
                            filedepth=self.filedepth + 1,
                        )
                    el._start_line = START

                    elements.append(
                        el
                    )
                    i += 1
                    continue

            # Переделываем ссылки на другие элементы
            m = self.re_reference.match(line)
            if m:
                
                START = i
                el = Reference(m.group()[1:])
                el._start_line = START
                elements.append(el)

                i += 1
                continue

            next_is_table = i + 1 < len(lines) and lines[i + 1].strip().startswith("|")

            if line.strip().startswith("|"):
                if not in_table:
                    START = i
                    in_table = True
                    tablelines = [line]
                else:
                    tablelines.append(line)

                if i == len(lines) - 1 or not next_is_table:
                    if len(tablelines) >= 2:
                        tab = Table(tablelines)
                        tab._is_initialized = False
                        tab._start_line = START
                        elements.append(tab)
                        in_table = False
                        tablelines = []
                i += 1
                continue

            else:
                if in_table:
                    START = i
                    if len(tablelines) >= 2:
                        
                        tab = Table(tablelines)
                        tab._start_line = START
                        tab._is_initialized = False
                        elements.append(tab)
                    in_table = False
                    tablelines = []
                    i += 1
                    continue

            next_is_quote = i + 1 < len(lines) and lines[i + 1].strip().startswith(">")

            if line.strip().startswith(">"):
                if not in_quote:
                    in_quote = True
                    quotelines = [line]
                else:
                    quotelines.append(line)

                if i == len(lines) - 1 or not next_is_quote:
                    if self.quotedepth >= Settings.Quote.max_quote_recursion:
                        raise RecursionError(
                            f"Maximum quote nesting quotedepth ({Settings.Quote.max_quote_recursion}) exceeded"
                        )
                    START = i

                    el = Quote.create(
                            quotelines=quotelines,
                            filename=self.filename,
                            parrentdir=self.parrentdir,
                            quotedepth=self.quotedepth + 1,
                        )

                    el._start_line = START 

                    elements.append(
                        el 
                    )
                    in_quote = False
                    quotelines = []
                i += 1
                continue

            else:
                if in_quote:
                    START = i
                    if self.quotedepth >= Settings.Quote.max_quote_recursion:
                        raise RecursionError(
                            f"Maximum quote nesting quotedepth ({Settings.Quote.max_quote_recursion}) exceeded"
                        )
                    el = Quote.create(
                            quotelines=quotelines,
                            filename=self.filename,
                            parrentdir=self.parrentdir,
                            quotedepth=self.quotedepth + 1,
                        )

                    el._start_line = START
                    
                    elements.append(
                        el 
                    )
                    in_quote = False
                    quotelines = []
                    i += 1
                    continue

                # ЗАГОЛОВКИ

            if Settings.Headline.parse:
                n = self.re_heading.match(line)
                if n:
                    START = i
                    level, line = n.groups()
                    el = Headline(len(level) - 1, line)
                    el._start_line = START
                    elements.append(el)
                    i += 1
                    continue

            START = i
            el = Paragraph(line)
            el._start_line = START
            elements.append(el)
            i += 1
            continue

            # Параграф
            paragraph_lines = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].strip().startswith(">")
                and not lines[i].strip().startswith("$$")
                and not lines[i].strip().startswith("#")
                and not lines[i].strip().startswith("|")
                and not lines[i].strip().startswith("```")
                and not lines[i].strip().startswith("-")
            ):
                paragraph_lines.append(lines[i])
                i += 1
            joined = "\n".join(line.strip() for line in paragraph_lines)
            elements.append(Paragraph(joined))

        self.elements = self._process_elements_list(elements)
