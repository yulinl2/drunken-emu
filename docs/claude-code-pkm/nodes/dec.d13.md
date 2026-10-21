---
id: dec.d13
kind: decision
status: DECIDED
title: "Done: the checks that close the PKM"
sources: [S13]
---

# Done: the checks that close the PKM

**Sources:** [S13](src.s13.md)

Done means all four hold, and each is checked by a command, not by judgement. (1) No node has status GAP. A gap is SUPERSEDED with the nodes that replace it, or DECIDED with a pointer to dec.d12. Check: the status column of build/src has no GAP. (2) Every in-scope page has a source node, and every table row and section heading on it is a new node or is already present as a node. Two kinds of row are not concepts and are not counted: an env row must be an UPPER_SNAKE variable name, and a shortcut row cannot be a bare number or more than five words. Generic headings such as Examples, Prerequisites and Next steps are not concepts either. Check: the coverage report that build/extract_pages.py prints, where the row and heading counts include only rows that pass these rules. (3) The English pages on the docs index are exactly the in-scope pages plus the pages in dec.d14. Check: dec.d14 is computed as the index minus the in-scope pages, and the script stops if an in-scope page is not on the index. (4) build_nodes.py --check and gen_tree.py --check both pass on the pushed head. Language indexes are not pages and are not counted.
