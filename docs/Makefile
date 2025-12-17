SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SOURCEDIR     = source
BUILDDIR      = _build
APIDIR        = $(SOURCEDIR)/_api
PROJECT       = omd2tex

.PHONY: help clean apidoc html

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@rm -rf "$(BUILDDIR)"
	@rm -rf "$(APIDIR)"

apidoc:
	@mkdir -p "$(APIDIR)"
	@$(SPHINXAPIDOC) -o "$(APIDIR)" "../$(PROJECT)" --separate

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route unknown targets to Sphinx
%:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
