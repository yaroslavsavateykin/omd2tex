import re
import yaml 

from .equation import Equation
from tools.search import find_file
from .paragraph import Paragraph
from .codeblock import CodeBlock
from .reference import Reference

class MarkdownParser:

    re_heading = re.compile(r'^(#{1,6})\s+(.*)')
    re_equation = re.compile(r'^\$\$(.*?)\$\$')
    re_table_row = re.compile(r'^\|(.+)\|$')
    re_image = re.compile(r'^!\[(.*?)\]\((.*?)\)')
    re_link = re.compile(r'^\[(.*?)\]\((.*?)\)')
    re_comment = re.compile(r'^<!--(.*?)-->$')
    re_footnote = re.compile(r'^\[\^(.+?)\]:\s+(.*)')
    re_codeblock_start = re.compile(r'^```(\w+)?$')
    
    #re_text_files1 = re.compile(r'!?\[\[([^\[\]#\|\^]+)(?:\|([^\[\]]+))?\]\]')
        
    re_text_files1 = re.compile(r'!?\[\[([^|\[\]]+?(?:\.(?:md|tex|txt))?)(?:\|([^\[\]]+))?\]\]')
    re_text_files2 = re.compile(r'!?\[([^\[\]]*)\]\(([^)]*?)(?:\.(md|tex|txt))?\)')

    re_reference = re.compile(r'\^([a-zA-Z0-9_-]+)')
    

    re_markdown_image = re.compile(r'!\[([^|\]]*?)(?:\|([^|\]]*?))?\]\(([^)]+)\)(?:\s*\^([a-zA-Z0-9_-]+))?')
    re_wiki_image = re.compile(r'!\[\[([^|\]]+?)(?:\|([^|\]]*?))?(?:\|([^|\]]*?))?\]\](?:\s*\^([a-zA-Z0-9_-]+))?')

    def __init__(self, 
                 filename: str, 
                 settings: dict,
                 parrentdir: str,
                 depth: int = 0) -> None:
        
        self.filename = filename
        self.parrentdir = parrentdir
        self.settings = settings
        self.depth = depth

        self.dir_filename = find_file(filename, search_path = settings['dir'])
        
        self.yaml = None
    
    @staticmethod    
    def _parse_size_parameter(size_str):
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

    def parse(self):
        
        
        from .file import File

        non_md_extensions = [
        ".jpg", ".jpeg", ".png", ".svg", ".gif",  # Изображения
        ".docx", ".pdf", ".xlsx", ".pptx",        # Документы
        ".zip", ".tar", ".gz",                    # Архивы
        ".mp3", ".mp4", ".avi", ".mov",           # Медиа
    ]

        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg"]

        with open(self.dir_filename, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        i = 0
        in_yaml = False 
        in_code_block = False
        in_equation = False 

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
                    i+=1 
                    continue
                else:
                    yaml_lines.append(line)
                    i += 1
                    continue
            
           


            # Extracting text files
            m = self.re_text_files1.match(line)
            if m:
                if self.depth >= self.settings["max_file_recursion"]:
                    raise RecursionError(f"Maximum file nesting depth ({self.settings["max_file_recursion"]}) exceeded")
                filename, _ = m.groups()
                
                if any(filename.endswith(ext) for ext in non_md_extensions): 
                    i += 1
                    continue
                
                if filename.startswith("#^"):
                    i += 1 
                    continue
                
                elements.append(File(filename + ".md" if not filename.endswith(".md") else filename, 
                                    self.settings, 
                                    parrentfilename=self.filename,
                                    parrentdir=self.parrentdir, 
                                    depth=self.depth + 1))
                i += 1
                continue

            n = self.re_text_files2.match(line)
            if n:
                if self.depth >= self.settings["max_file_recursion"]:
                    raise RecursionError(f"Maximum file nesting depth ({self.settings["max_file_recursion"]}) exceeded")
                _, filename, extension = n.groups()
                
                if filename.startswith("#^"):
                    i += 1 
                    continue
                if any(filename.endswith(ext) for ext in non_md_extensions): 
                    i += 1
                    continue
                
                if extension:
                    full_filename = f"{filename}.{extension}"
                else:
                    full_filename = filename + ".md" if not filename.endswith(".md") else filename
                
                elements.append(File(full_filename, 
                                    self.settings, 
                                    parrentfilename=self.filename,
                                    parrentdir=self.parrentdir,
                                    depth=self.depth + 1))
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
                
                width, height =self._parse_size_parameter(size_param)
                caption = alt_text if alt_text else None
                
                image_obj = Image(filename=filename,
                                parrentfilename=self.filename,
                                caption=caption,
                                width=width,
                                height=height,
                                settings=self.settings)
                print("Да") 
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
                    width, height =self._parse_size_parameter(param2)
                    if width is not None:
                        reference = param1 if param1 else None
                    else:
                        width, height =self._parse_size_parameter(param1)
                        if width is None:
                            reference = param1 if param1 else None
                            caption = param2 if param2 else None
                        else:
                            caption = param2 if param2 else None
                else:
                    if param1:
                        width, height =self._parse_size_parameter(param1)
                        if width is None:
                            reference = param1
                
                image_obj = Image(filename=filename,
                                parrentfilename=self.filename,
                                caption=caption,
                                width=width,
                                height=height,
                                settings=self.settings)
                
                if reference:
                    image_obj.reference = reference
                
                if ref_link:
                    image_obj.reference = ref_link
                
                elements.append(image_obj)
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
                        elements.append(CodeBlock(blocktype, blocklines, settings=self.settings["codeblocks"]))
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



            # Параграф
            paragraph_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip():
                paragraph_lines.append(lines[i])
                i += 1
            joined = '\n'.join(l.strip() for l in paragraph_lines)
            elements.append(Paragraph(joined))

        return elements




