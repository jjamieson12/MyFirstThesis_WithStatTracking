.PHONY: clean keep_comment minimal quick content qcontent quietly

#EXTRASTYS = abhepexpt.sty abhep.sty abmath.sty lineno.sty siunitx.sty SIunits.sty varwidth.sty #Add extra styles if you wish
QPDFLATEX = pdflatex -halt-on-error -interaction=nonstopmode


JJthesis.pdf: JJthesis.tex preamble.tex Section_*/*.tex frontmatter.tex backmatter.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	(pdflatex JJthesis && bibtex JJthesis && pdflatex JJthesis && pdflatex JJthesis) || rm -f JJthesis.pdf
	@rm -f JJthesis.{aux,toc,lof,lot}
	@rm -f comment.cut

JJthesis_Quiet.pdf: JJthesis.tex preamble.tex Section_*/*.tex frontmatter.tex backmatter.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	#(pdflatex JJthesis && bibtex JJthesis && pdflatex JJthesis && pdflatex JJthesis) || rm -f JJthesis.pdf
	($(QPDFLATEX) JJthesis && bibtex JJthesis && $(QPDFLATEX) JJthesis && $(QPDFLATEX) JJthesis) > LaTeXErrors.txt || rm -f JJthesis.pdf
	@echo "Errors are:"
	@grep '^!.*' --color=always LaTeXErrors.txt || echo "There are no errors :)"
	@rm -f LaTeXErrors.txt
	@rm -f JJthesis.{aux,toc,lof,lot}
	@rm -f comment.cut

JJthesis_minimal.pdf: JJthesis.tex preamble.tex Section_*/*.tex frontmatter.tex backmatter.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot,log,blg,bbl,out}
	(pdflatex JJthesis && bibtex JJthesis && pdflatex JJthesis && pdflatex JJthesis) || rm -f JJthesis.pdf
	@rm -f JJthesis.{aux,toc,lof,lot,log,blg,bbl,out}
	@rm -f comment.cut

JJthesis_WithComments.pdf: JJthesis.tex preamble.tex Section_*/*.tex frontmatter.tex backmatter.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	(pdflatex JJthesis && bibtex JJthesis && pdflatex JJthesis && pdflatex JJthesis) || rm -f JJthesis.pdf
	@rm -f JJthesis.{aux,toc,lof,lot}

JJthesis_NoRef.pdf: JJthesis.tex preamble.tex Section_*/*.tex frontmatter.tex backmatter.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	(pdflatex JJthesis) || rm -f JJthesis.pdf
	@rm -f JJthesis.{aux,toc,lof,lot}
	@rm -f comment.cut

JJthesis_ContentOnly.pdf: JJthesis_min.tex preamble.tex Section_*/*.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	@rm -f JJthesis_min.{aux,toc,lof,lot,log,blg,bbl,out}
	(pdflatex JJthesis_min) || rm -f JJthesis_min.pdf
	@rm -f JJthesis_min.{aux,toc,lof,lot,log,blg,bbl,out}
	@rm -f comment.cut
	@mv JJthesis_min.pdf JJthesis.pdf

JJthesis_qContentOnly.pdf: JJthesis_min.tex preamble.tex Section_*/*.tex appendices.tex
	@rm -f JJthesis.{aux,toc,lof,lot}
	@rm -f JJthesis_min.{aux,toc,lof,lot,log,blg,bbl,out}
	$(QPDFLATEX) JJthesis_min > LaTeXErrors.txt || rm -f JJthesis_min.pdf
	@echo "Errors are:"
	@grep '^!.*' --color=always LaTeXErrors.txt || echo "There are no errors :)"
	@rm -f LaTeXErrors.txt
	@rm -f JJthesis_min.{aux,toc,lof,lot,log,blg,bbl,out}
	@rm -f comment.cut
	@mv JJthesis_min.pdf JJthesis.pdf || echo "failed to make :("

clean:
	@rm -f JJthesis.pdf JJthesis.log JJthesis.aux
	@rm -f *.bbl *.blg *.lof *.cut
	@rm -f *.lot *.out *.toc

keep_comments:
	@make JJthesis_WithComments.pdf

minimal:
	@make JJthesis_minimal.pdf

quick:
	@make JJthesis_NoRef.pdf

content:
	@make JJthesis_ContentOnly.pdf

qcontent:
	@make JJthesis_qContentOnly.pdf

quietly:
	@make JJthesis_Quiet.pdf
