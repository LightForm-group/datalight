# Makefile for Sphinx documentation
#

# Convert svg to pdf for latex creation
SOURCEDIR     = source
#IMAGEDIRS can be a list of directories that contain SVG files and are relative to the SOURCEDIR
IMAGEDIRS      = ../images

# SVG to PDF conversion
SVG2PDF       = inkscape
SVG2PDF_FLAGS =

# Pattern rule for converting SVG to PDF
%.pdf : %.svg
	$(SVG2PDF) -f $< -A $@

# Build a list of SVG files to convert to PDFs
PDFs := $(foreach dir, $(IMAGEDIRS), $(patsubst %.svg,%.pdf,$(wildcard $(SOURCEDIR)/$(dir)/*.svg)))

# Make a rule to build the PDFs
images: $(PDFs)

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

# Define where the gh-pages will be build
ifeq ($(strip $(GITHUBBUILDDIR)),)
GITHUBBUILDDIR = ../$(notdir $(CURDIR))-html
endif

# Define github repository to commit
GITREPO = https://github.com/MechMicroMan/datalight

PDFBUILDDIR   = /tmp

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf pdf text man changes linkcheck doctest

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  dirhtml   to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  pickle    to make pickle files"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  qthelp    to make HTML files and a qthelp project"
	@echo "  devhelp    to make HTML files and a Devhelp project"
	@echo "  epub       to make an epub"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  pdf        to make PDF file with rst2pdf package"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  changes   to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo "  doctest   to run all doctests embedded in the documentation (if enabled)"

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

#Download plantum.jar for UML graph (or other)
plantuml.jar:
	#curl -s -S -L -f https://downloads.sourceforge.net/project/plantuml/$@ -z $@ -o $@.tmp && mv -f $@.tmp $@ 2>/dev/null || rm -f $@.tmp $@
	#mv $@ utils/
	[ -f utils/plantuml.jar ] && echo "plantuml.jar exist" || wget -c https://downloads.sourceforge.net/project/plantuml/$@
	mkdir -p utils
	mv $@ utils/ && echo "plantuml.jar installed" || echo "plantuml.jar already present"

gh-pages: $(PDFs) plantuml.jar
ifeq ($(strip $(GITREPO)),)
	$(error Please define the git repository for the Gh-pages)
endif

	if [ ! -d $(GITHUBBUILDDIR) ]; then \
	git clone $(GITREPO) $(GITHUBBUILDDIR) ;\
	cd $(GITHUBBUILDDIR);\
	git branch gh-pages;\
	git symbolic-ref HEAD refs/heads/gh-pages;\
	rm .git/index;\
	git clean -fdx;\
	fi
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(GITHUBBUILDDIR)
	@echo
	@echo "Build finished. The HTML pages are in $(GITHUBBUILDDIR)."
	@echo "Update gh-pages and push to github"
	cd $(GITHUBBUILDDIR) ; git add . ; git commit -m "rebuilt docs" ; git push origin gh-pages

#	git checkout -b gh-pages remotes/origin/gh-pages; \



pickle:
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(BUILDDIR)/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

json:
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) $(BUILDDIR)/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(BUILDDIR)/htmlhelp."

qthelp:
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS) $(BUILDDIR)/qthelp
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in $(BUILDDIR)/qthelp, like this:"
	@echo "# qcollectiongenerator $(BUILDDIR)/qthelp/javalambredocumentation.qhcp"
	@echo "To view the help file:"
	@echo "# assistant -collectionFile $(BUILDDIR)/qthelp/javalambredocumentation.qhc"

devhelp:
	$(SPHINXBUILD) -b devhelp $(ALLSPHINXOPTS) $(BUILDDIR)/devhelp
	@echo
	@echo "Build finished."
	@echo "To view the help file:"
	@echo "# mkdir -p $$HOME/.local/share/devhelp/test"
	@echo "# ln -s $(BUILDDIR)/devhelp $$HOME/.local/share/devhelp/test"
	@echo "# devhelp"

epub:
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latex: $(PDFs)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

latexpdf: $(PDFs)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	make -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

pdf:
	$(SPHINXBUILD) -b pdf $(ALLSPHINXOPTS) $(BUILDDIR)/pdf
	@echo
	@echo "Build finished. The PDF files are in $(BUILDDIR)/pdf."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

clean:
	-rm -rf $(BUILDDIR)/*
	-rm $(PDFs)
