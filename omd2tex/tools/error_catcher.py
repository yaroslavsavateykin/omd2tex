import shutil
import time
from typing import Union, List, Any
import subprocess
import os


from ..objects.base import BaseClass
from ..objects import Frame
from ..objects.document import Document
from ..objects.file import File
from ..objects.list import List as MDList
from .settings import Settings
from .markdown_parser import MarkdownParser


class ConsoleColors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @staticmethod
    def true_false_color(statement: bool):
        if statement:
            return f"{ConsoleColors.GREEN}True{ConsoleColors.END}"
        else:
            return f"{ConsoleColors.RED}{False}{ConsoleColors.END}"


class ObjectImage:
    def __init__(self, md_object, filename="", source_str=""):
        self.object = md_object
        self.filename = filename
        self.source_str = source_str
        self.compile_success = "Not compiled"
        self.stdout = ""

    def __str__(self):
        status = f"""
CompileError:
    Compile status: {ConsoleColors.RED}{self.compile_success}{ConsoleColors.END}
    Source:         {self.source_str}
    Filename:       {self.filename}
    Line:           {self.object._start_line}
    Object:         {self.object}
    LaTeX:\n{ConsoleColors.CYAN}{self.object.to_latex()}{ConsoleColors.END}"""

        #         status = f"""
        # CompileError:
        #     Compile status: {self.compile_success}
        #     Source:         {self.source_str}
        #     Filename:       {self.filename}
        #     Line:           {self.object._start_line}
        #     Object:         {self.object}
        #     LaTeX:\n{self.object.to_latex()}"""
        return status

    def __dict__(self):
        obj_dict = {
            "object": self.object,
            "filename": self.filename,
            "source": self.source_str,
            "success": self.compile_success,
            "stdout": self.stdout,
        }

        return obj_dict


class ErrorCompileCatcher:
    def __init__(self, md_object: Union[Document, File, MarkdownParser, List[Any]]):
        # self.objects = []

        self.file = None

        if isinstance(md_object, Document):
            if md_object.file.elements:
                # self.objects = md_object.file.elements
                # self.objects = [
                #     ObjectImage(md_object=x, source_str=md_object.filename)
                #     for x in self.objects
                # ]
                self.file = md_object.file
            else:
                self.file = File()

        elif isinstance(md_object, File):
            # self.objects = md_object.elements
            # self.objects = [
            #     ObjectImage(md_object=x, source_str=md_object.filename)
            #     for x in self.objects
            # ]
            self.file = md_object

        elif isinstance(md_object, MarkdownParser):
            # self.objects = md_object.elements
            # self.objects = [
            #     ObjectImage(md_object=x, source_str=md_object.filename)
            #     for x in self.objects
            # ]
            self.file = File().from_elements(md_object.elements)
        elif issubclass(type(md_object), BaseClass):
            # self.objects = [
            #     ObjectImage(md_object=md_object, source_str="single_object")
            # ]
            self.file = File().from_elements([md_object])
        elif isinstance(md_object, list):
            objects = [x for x in md_object if issubclass(x, BaseClass)]

            self.file = File().from_elements(objects)

            # self.objects = [
            #     ObjectImage(md_object=x, source_str="list_of_objects")
            #     for x in self.objects
            # ]
        self.file = ObjectImage(
            md_object=self.file,
            filename="ObjectImage",
            source_str="ObjectImage",
        )

    @staticmethod
    def _recursive_opener(objects: Union[ObjectImage, List[ObjectImage]]):
        if isinstance(objects, ObjectImage):
            objects = [objects]

        new_list = []

        for obj in objects:
            if isinstance(obj.object, Document):
                doc_list = [
                    ObjectImage(
                        md_object=x,
                        source_str=obj.source_str + " -> Document" + str(type(obj)),
                        filename=obj.filename + " -> " + obj.object.filename,
                    )
                    for x in obj.object.file.elements
                ]

                new_list += doc_list

                doc_list = []

            elif isinstance(obj.object, File):
                # print(obj.object.elements)
                file_list = [
                    ObjectImage(
                        md_object=x,
                        source_str=obj.source_str + " -> File",
                        filename=obj.filename + " -> " + obj.object.filename,
                    )
                    for x in obj.object.elements
                ]

                new_list += file_list

                file_list = []

            elif isinstance(obj.object, MarkdownParser):
                md_parser_list = [
                    ObjectImage(
                        md_object=x,
                        source_str=obj.source_str + " -> MarkdownParser",
                        filename=obj.filename + " -> " + obj.object.filename,
                    )
                    for x in obj.object.elements
                ]

                new_list += md_parser_list

                md_parser_list = []
            elif isinstance(obj.object, Frame):
                frame_list = [
                    ObjectImage(
                        md_object=x,
                        source_str=obj.source_str + " -> Frame",
                        filename=obj.filename + " -> " + obj.object.title,
                    )
                    for x in obj.object.elements
                ]
                new_list += frame_list
            # elif issubclass(type(obj.object), MDList):
            #     items_list = [
            #         ObjectImage(
            #             md_object=x,
            #             source_str=obj.source_str + " -> List",
            #             filename=obj.filename,
            #         )
            #         for x in obj.object.items
            #     ]
            #
            #     print(items_list)
            #
            #     new_list += items_list
            #
            #     if obj.object.merged:
            #         merged_list = [
            #             ObjectImage(
            #                 md_object=x,
            #                 source_str=obj.source_str + " -> List",
            #                 filename=obj.filename,
            #             )
            #             for x in obj.object.merged
            #         ]
            #
            #         new_list += merged_list
            else:
                new_list.append(obj)

        if any(
            [
                (
                    isinstance(obj.object, Document)
                    or isinstance(obj.object, File)
                    or isinstance(obj.object, MarkdownParser)
                    or isinstance(obj.object, Frame)
                    # or (
                    #     bool(obj.object.items)
                    #     if issubclass(type(obj.object), MDList)
                    #     else 0
                    # )
                    # or (
                    #     bool(obj.object.merged)
                    #     if issubclass(type(obj.object), MDList)
                    #     else 0
                    # )
                )
                for obj in new_list
            ]
        ):
            return ErrorCompileCatcher._recursive_opener(new_list)
        else:
            return new_list

    @staticmethod
    def _recursive_compiler(
        objects: List[ObjectImage],
        batch: int = None,
        total_errors=1,
        rmdir=False,
        print_analyzing=True,
        timeout=15,
    ):
        def chunk_list(lst, chunk_size):
            return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

        length = len(objects)

        if not batch:
            batch = int(0.3 * length)
            if not batch:
                batch = 1

        objects1 = chunk_list(objects, batch)

        current_dir = os.getcwd()
        export_dir = os.path.join(current_dir, "error_catcher")
        try:
            if rmdir:
                os.remove(export_dir)
        except:
            pass

        os.makedirs(export_dir, exist_ok=True)
        Settings.Export.export_dir = export_dir

        start = time.time()

        errors_found = 0
        for i, obj in enumerate(objects1):
            comp_time_start = time.time()

            doc = Document().from_elements([x.object for x in obj])

            doc.to_latex_file()

            # doc.check()

            try:
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-shell-escape",
                        "-interaction=nonstopmode",
                        doc.filename + ".tex",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=export_dir,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                )
            except UnicodeDecodeError:
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-shell-escape",
                        "-interaction=nonstopmode",
                        doc.filename + ".tex",
                    ],
                    capture_output=True,
                    cwd=export_dir,
                    timeout=timeout,
                )
                stdout = result.stdout.decode("utf-8", errors="replace")
                stderr = result.stderr.decode("utf-8", errors="replace")
                result.stdout = stdout
                result.stderr = stderr

            has_critical_errors = (
                result.returncode != 0  # Код возврата не 0
                or "error" in result.stderr.lower()  # Есть ошибки в stderr
                or "emergency stop"
                in result.stdout.lower()  # Критические ошибки в stdout
            )

            # if result.stderr == 1:
            if has_critical_errors:
                for j, ob in enumerate(obj):
                    comp_time_start = time.time()

                    doc = Document().from_elements([ob.object])

                    doc.to_latex_file()

                    # doc.check()

                    try:
                        result = subprocess.run(
                            [
                                "pdflatex",
                                "-shell-escape",
                                "-interaction=nonstopmode",
                                doc.filename + ".tex",
                            ],
                            capture_output=True,
                            text=True,
                            cwd=export_dir,
                            encoding="utf-8",
                            errors="replace",
                            timeout=timeout,
                        )
                    except UnicodeDecodeError:
                        result = subprocess.run(
                            [
                                "pdflatex",
                                "-shell-escape",
                                "-interaction=nonstopmode",
                                doc.filename + ".tex",
                            ],
                            capture_output=True,
                            cwd=export_dir,
                            timeout=timeout,
                        )
                        stdout = result.stdout.decode("utf-8", errors="replace")
                        stderr = result.stderr.decode("utf-8", errors="replace")
                        result.stdout = stdout
                        result.stderr = stderr

                    # print(result.stdout)
                    comp_time_end = time.time()

                    if result.returncode == 1:
                        ob.stdout = result.stdout
                        ob.compile_success = False
                        errors_found += 1

                    else:
                        ob.compile_success = True

                    proc = ((i) * batch + j + 1) / length * 100

                    if print_analyzing:
                        returncode = True if result.returncode != 1 else False
                        print(
                            f"{proc:.2f}% checked |",
                            doc.filename + ".tex |",
                            f"result: {ConsoleColors.true_false_color(returncode)} |",
                            f"time: {(comp_time_end - comp_time_start):.2f} seconds",
                        )

                    if total_errors <= errors_found:
                        return objects

            else:
                for ob in obj:
                    ob.compile_success = True

            comp_time_end = time.time()

            if i + 1 == len(objects1):
                proc = 100
            else:
                proc = (i + 1) * batch / length * 100

            if print_analyzing:
                returncode = True if result.returncode != 1 else False
                print(
                    f"{proc:.2f}% checked |",
                    doc.filename + ".tex |",
                    f"result: {ConsoleColors.true_false_color(returncode)} |",
                    f"time: {(comp_time_end - comp_time_start):.2f} seconds",
                )

        if rmdir:
            shutil.rmtree(export_dir)

        end = time.time()

        if print_analyzing:
            print(f"Total time used: {(end - start):.2f} seconds")

        return objects

    def analyze(
        self,
        batch: int = None,
        total_errors=1,
        rmdir=True,
        print_analyzing=True,
    ):
        from .globals import Global

        Global.ERROR_CATCHER = False

        objects = self._recursive_opener([self.file])

        objects = self._recursive_compiler(
            objects,
            batch=batch,
            total_errors=total_errors,
            rmdir=rmdir,
            print_analyzing=print_analyzing,
        )

        error = False

        error_objects = []

        for obj in objects:
            if not obj.compile_success:
                error = True

                error_objects.append(obj)

        if print_analyzing:
            if error:
                print("\nError found, see report:")
                for er_ob in error_objects:
                    print(er_ob)
            else:
                print("No errors found. :)")

        Global.ERROR_CATCHER = False

        return error_objects
