# drunken-emu — the figure bank's recurring procedures. The React harness (bin/emu) has its own entry point.
.PHONY: figbank-test page-variable-model figpipe-fixture ledger ledger-check

figbank-test:        ## the bank's own gates: renderer, budget/overflow/ellipsis gates, React host, text calibration (node, no browser)
	node --test figbank/tests/*.test.js

page-variable-model: ## build the variable-model page's React shell -> $(OUT)/variable-model.html (needs node + pnpm; MetaProof's `make page` calls this with OUT=figures/shell)
	mkdir -p $(OUT)
	bash figbank/app/bundle.sh figbank/app/variable-model $(OUT)/variable-model.html

figpipe-fixture:     ## run the whole pipeline on the fixture figure, reader off (needs Python playwright + Chromium)
	bin/figpipe figbank/tests/fixture-two-regions.json --out out --reader none --no-pdf

ledger:              ## regenerate figbank/LEDGER.md + ledger.json from every reachable verdicts.jsonl
	python3 bin/gen_ledger.py --write

ledger-check:        ## assert this repo's own ledger rows are not stale relative to figbank/examples/verdicts.jsonl
	python3 bin/gen_ledger.py --check

OUT ?= out
