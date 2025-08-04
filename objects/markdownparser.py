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

    def __init__(self, 
                 filename: str, 
                 settings: dict,
                 depth: int = 0) -> None:
        
        self.filename = filename
        self.settings = settings
        self.depth = depth

        self.dir_filename = find_file(filename, search_path = settings['dir'])
        
        self.yaml = None
    

    def parse(self):
        
        
        from .file import File

        non_md_extensions = [
        ".jpg", ".jpeg", ".png", ".svg", ".gif",  # Изображения
        ".docx", ".pdf", ".xlsx", ".pptx",        # Документы
        ".zip", ".tar", ".gz",                    # Архивы
        ".mp3", ".mp4", ".avi", ".mov",           # Медиа
    ]


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
                                     depth = self.depth + 1))
                i += 1
                continue

            n = self.re_text_files2.match(line)
            if n:
                if self.depth >= self.settings["max_file_recursion"]:
                    raise RecursionError(f"Maximum file nesting depth ({self.settings["max_file_recursion"]}) exceeded")

                _, filename  = n.groups()
                
                if filename.startswith("#^"):
                    i += 1 
                    continue



                if any(filename.endswith(ext) for ext in non_md_extensions): 
                    i += 1
                    continue
                
                elements.append(File(filename + ".md" if not filename.endswith(".md") else filename, 
                                     self.settings, 
                                     parrentfilename=self.filename,
                                     depth = self.depth + 1))
                i += 1
                continue
            

            # БЛОКИ КОДА
            if line.startswith("```") and not in_code_block:
                # Начало блока кода
                blocktype = line.strip("```").strip()
                blocklines = []
                in_code_block = True
                i += 1
                continue

            if in_code_block:
                if line.startswith("```"):
                    if blocklines:  # Проверка на пустые блоки
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
            if line.strip().startswith("$$"):
                if not in_equation:
                    equationlines = []
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



"""
            if in_code_block:
                if line.strip() == '```':
                    self.elements.append(CodeBlock(code_lang, code_lines))
                    in_code_block = False
                    code_lang = ""
                    code_lines = []
                else:
                    code_lines.append(line)
                i += 1
                continue

            m = self.re_codeblock_start.match(line)
            if m:
                in_code_block = True
                code_lang = m.group(1) or ""
                code_lines = []
                i += 1
                continue

            m = self.re_heading.match(line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                self.elements.append(Heading(level, text))
                i += 1
                continue

            m = self.re_equation.match(line)
            if m:
                self.elements.append(Equation(m.group(1).strip()))
                i += 1
                continue

            if self.re_table_row.match(line):
                header = [c.strip() for c in line.strip('|').split('|')]
                i += 1
                if i < len(lines):
                    i += 1  # пропускаем разделитель таблицы
                rows = []
                while i < len(lines) and self.re_table_row.match(lines[i]):
                    row = [c.strip() for c in lines[i].strip('|').split('|')]
                    rows.append(row)
                    i += 1
                self.elements.append(Table(header, rows))
                continue

            m = self.re_image.match(line)
            if m:
                alt, path = m.groups()
                self.elements.append(Image(path.strip(), alt.strip()))
                i += 1
                continue

            m = self.re_link.match(line)
            if m:
                text, href = m.groups()
                self.elements.append(Link(text.strip(), href.strip()))
                i += 1
                continue

            m = self.re_comment.match(line)
            if m:
                self.elements.append(Comment(m.group(1).strip()))
                i += 1
                continue

            m = self.re_footnote.match(line)
            if m:
                label, foot_text = m.groups()
                self.elements.append(Footnote(label.strip(), foot_text.strip()))
                i += 1
                continue

            if not line.strip():
                i += 1
                continue
"""
