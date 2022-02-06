.PHONY: all clean

FILE = rpz_cvetkov

all:
	pdflatex $(FILE).tex

	bibtex $(FILE).aux

	pdflatex $(FILE).tex
	pdflatex $(FILE).tex
	
	xdg-open $(FILE).pdf


clean:
	echo "Coming soon..."
