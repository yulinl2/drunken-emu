# drunken-emu — the figure bank's recurring procedures. The React harness (bin/emu) has its own entry point.
.PHONY: figbank-test page-variable-model page-frontier-tree figpipe-fixture

figbank-test:        ## the bank's own gates: renderer, budget/overflow/ellipsis gates, React host, text calibration (node, no browser)
	node --test figbank/tests/*.test.js

page-variable-model: ## build the variable-model page's React shell -> $(OUT)/variable-model.html (needs node + pnpm; MetaProof's `make page` calls this with OUT=figures/shell)
	mkdir -p $(OUT)
	bash figbank/app/bundle.sh figbank/app/variable-model $(OUT)/variable-model.html

page-frontier-tree:  ## build the tree + click-for-detail page shell -> $(OUT)/frontier-tree.html (needs node + pnpm; a consuming repo's own script injects its tree data, issue #12)
	mkdir -p $(OUT)
	bash figbank/app/bundle.sh figbank/app/frontier-tree $(OUT)/frontier-tree.html

figpipe-fixture:     ## run the whole pipeline on the fixture figure, reader off (needs Python playwright + Chromium)
	bin/figpipe figbank/tests/fixture-two-regions.json --out out --reader none --no-pdf

OUT ?= out
