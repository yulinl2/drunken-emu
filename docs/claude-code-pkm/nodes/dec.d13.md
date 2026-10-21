---
id: dec.d13
kind: decision
status: DECIDED
title: "Done: the checks that close the PKM"
sources: [S13]
---

# Done: the checks that close the PKM

**Sources:** [S13](src.s13.md)

Done means all four hold, and each is checked by a command, not by judgement. (1) No node has status GAP. A gap is SUPERSEDED with the nodes that replace it, or DECIDED with a pointer to dec.d12. Check: grep for the GAP status over build/src finds nothing. (2) Every in-scope page has a source node, and every table row and section heading on it is a new node or is already present as a node. Check: the coverage report that build/extract_pages.py prints. (3) The English pages on the docs index are exactly the in-scope pages plus the pages in dec.d14. Check: dec.d14 is computed as the index minus the in-scope pages, and the script stops if an in-scope page is not on the index. (4) build_nodes.py --check and gen_tree.py --check both pass on the pushed head. A concept is a table row or a section heading (levels 2 to 4) on an in-scope page. Generic headings such as Examples, Prerequisites and Next steps are not concepts. Language indexes are not pages and are not counted.
