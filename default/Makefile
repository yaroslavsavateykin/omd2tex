all: python compile #open 

backup:
	rm -r ~/.mdconvert_backup/
	cp -r ../.mdconvert/ ~/.mdconvert_backup/

python:
	rm -f file.tex 
	python main.py  # Генерирует main.tex

compile:  
	rm -f file.pdf
	rm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml
	pdflatex -shell-escape file.tex 
	biber file      # Используем имя файла БЕЗ расширения .tex!
	pdflatex -shell-escape file.tex
	pdflatex -shell-escape file.tex
	rm -rf _minted*
	rm -f *.bib *.bbl *.blg *.aux *.log *.out *.toc *.bcf *.run.xml

open:
	xdg-open file.pdf

clean:
	rm -f file.tex file.pdf *.aux *.log *.out *.toc *.ps
	rm -f support/*.png
	rm -rf _minted*
	rm -f *.bib *.bcf *.run.xml *.bbl *.blg
