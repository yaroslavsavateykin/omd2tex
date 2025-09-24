from ..tools import Global
import os


class Makefile:
    @classmethod
    def to_string(cls):
        if Global.CITATION_INITIALIZED:
            biber = "\n\tbiber main # Используем имя файла БЕЗ расширения .tex!\n\tpdflatex -shell-escape main.tex\n\tpdflatex -shell-escape main.tex"
        elif Global.REFERENCE_DICT:
            biber = "\n\tpdflatex -shell-escape main.tex"
        else:
            biber = ""

        string = f"""all: compile

python:
\trm -f main.tex
\tpython main.py

compile:
\trm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml
\tpdflatex -shell-escape main.tex{biber}
\trm -rf _minted*
\trm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml
\tmv main.pdf {Global.DOCUMENT_NAME}.pdf

open:
\txdg-open main.pdf

clean:
\trm -f main.pdf *.aux *.log *.out *.toc *.ps
\trm -rf _minted*
\trm -f *.bib *.bcf *.run.xml *.bbl *.blg
"""
        return string

    @classmethod
    def to_file(cls, directory="."):
        """Записывает Makefile в указанную директорию"""
        filepath = os.path.join(directory, "Makefile")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cls.to_string())
        return filepath
