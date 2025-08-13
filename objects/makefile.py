class Makefile:
    def __init__(self, settings) -> None:
        self.settings = settings

    def to_string(self):
        string = """
all: compile  

backup:
	rm -r ~/.mdconvert_backup/
	cp -r ../.mdconvert/ ~/.mdconvert_backup/

python:
	rm -f main.tex 
	python main.py  # Генерирует main.tex

compile:  
	rm -f main.pdf
	rm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml
	pdflatex -shell-escape main.tex 
	biber main      # Используем имя файла БЕЗ расширения .tex!
	pdflatex -shell-escape main.tex
	pdflatex -shell-escape main.tex
	rm -rf _minted*
	rm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml

open:
	xdg-open main.pdf

clean:
	rm -f main.pdf *.aux *.log *.out *.toc *.ps
	rm -f support/*.png
	rm -rf _minted*
	rm -f *.bib *.bcf *.run.xml *.bbl *.blg
"""

    return string
