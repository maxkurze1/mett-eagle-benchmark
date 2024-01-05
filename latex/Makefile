.DEFAULT_GOAL := rebuild

.PHONY: rebuild
rebuild: clean plots.pdf

plots.pdf: $(wildcard *.tex)
	latexmk -pdflua plots.tex

.PHONY: clean
clean:
	latexmk -C
