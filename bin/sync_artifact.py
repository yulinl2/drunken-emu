#!/usr/bin/env python3
"""sync_artifact.py — turn a claude.ai single-file React artifact (.jsx) into
a browser-runnable app.jsx for the local harness.

What it does (and the reason each step exists):
  1. Strip `import` statements       — the harness has no bundler; React/ReactDOM
                                       are globals loaded from vendor/*.js.
  2. Re-bind named hook imports      — `import { useState } from "react"` becomes
                                       a `const {...} = React` destructure so the
                                       artifact's own identifiers keep working.
  3. Strip `export default`          — Babel-standalone compiles a plain <script>,
                                       not an ES module; the component must be a
                                       top-level function instead.
  4. Append a ReactDOM.createRoot    — something has to mount the component; the
     mount call                        artifact itself never does (claude.ai does).
  5. Fail loudly on bare imports     — a line-start import of anything not in
     we cannot satisfy                 SUPPORTED (lucide-react, recharts, …) will
                                       NOT render here; better a named error now
                                       than a blank page later. The check is a text
                                       match, not a parser: see the list below.

What the text match does not see (each pinned in checks/test_sync_artifact.py; measured 2026-10-14; exit 0, and
the artifact can then break in the browser): a comment between `from` and the module, an import that does not
start its line, `import()`, `export ... from`. Import-like text that starts a line inside a comment or a template
literal is taken for an import. An aliased hook (`import { useState as us }`) is emitted as
`const {useState, useState as us} = React;`, a syntax error, and a namespace import (`import * as R`) leaves
`R` undefined.

Usage: sync_artifact.py <artifact.jsx> <out_app.jsx>
Exit 0 on success; exit 2 with a dependency list if a line-start import names a
module this kit does not vendor.
"""
import re
import sys

SUPPORTED = {"react", "react-dom", "react-dom/client"}

# one definition of "an import statement", used by the guard, the re-binding and the stripping: it may span lines
# (`import {\n a,\n b\n} from "x"`), may carry a default beside the braces (`import R, { a } from "x"`), or have no clause
# at all (`import "x"`); the rest of its last line goes with it
IMPORT = re.compile(r'^import\b\s*(?:(?P<clause>[^\'";]+?)\s*from\s*)?(?P<q>["\'])(?P<mod>[^"\']+)(?P=q)[^\n]*', re.M)

def main(src_path: str, out_path: str) -> int:
    import os as _os
    if _os.path.realpath(src_path) == _os.path.realpath(out_path):
        sys.stderr.write('refuse: src == dst - sync is not idempotent; '
                         'double-processing duplicates hook rebinds and the mount call. exit 2\n')
        return 2

    src = open(src_path, encoding="utf-8").read()

    # 5. dependency boundary check, before any rewriting
    deps = {m.group("mod") for m in IMPORT.finditer(src)}
    unsupported = sorted(d for d in deps if d not in SUPPORTED)
    if unsupported:
        print("UNSUPPORTED_IMPORTS:", ", ".join(unsupported))
        print("This harness vendors only React/ReactDOM/Tailwind/Babel; "
              "artifacts importing the modules above will not render in it.")
        return 2

    # 2. collect named react imports so we can re-bind them
    named = set()
    for m in IMPORT.finditer(src):
        braces = re.search(r"{([^}]*)}", m.group("clause") or "")
        if m.group("mod") == "react" and braces:
            named |= {t.strip() for t in braces.group(1).split(",") if t.strip()}
    # hooks used without import (artifact may rely on claude.ai transform)
    named |= set(re.findall(r'\b(use[A-Z]\w+|createContext|Fragment)\b', src)) & {
        "useState", "useEffect", "useRef", "useMemo", "useCallback",
        "useContext", "useReducer", "useLayoutEffect", "createContext", "Fragment",
    }

    # 1. strip every import statement whole (it can span lines); its newlines stay, so line numbers below it do not move
    body = IMPORT.sub(lambda m: "\n" * m.group(0).count("\n"), src)
    # ...then any line still starting with `import` is one the statement matcher does not parse (a comment between `from`
    # and the module, say). The harness cannot run an import, so none may stay: this is what the old stripping did alone.
    body = re.sub(r"^import\s[^\n]*$", "", body, flags=re.M)

    # 3. strip export default; the name it carried IS the root component
    root_name = None
    m_def = re.search(r"^export\s+default\s+function\s+(\w+)", body, flags=re.M)
    if m_def:
        root_name = m_def.group(1)
        body = re.sub(r"^export\s+default\s+function\s+(\w+)", r"function \1", body, flags=re.M)
    else:
        tail_export = re.search(r"^export\s+default\s+(\w+)\s*;?\s*$", body, flags=re.M)
        if tail_export:
            root_name = tail_export.group(1)
            body = body.replace(tail_export.group(0), "")
        else:
            # no export at all: fall back to the last top-level function declaration
            all_fns = re.findall(r"^function\s+(\w+)\s*\(", body, flags=re.M)
            root_name = all_fns[-1] if all_fns else None
    if not root_name:
        print("NO_ROOT_COMPONENT: could not find a top-level function component")
        return 2

    prelude = "const {%s} = React;\n" % ", ".join(sorted(named)) if named else ""
    mount = ("\n\nconst __root = ReactDOM.createRoot(document.getElementById('root'));"
             f"__root.render(React.createElement({root_name}));\n")
    open(out_path, "w", encoding="utf-8").write(prelude + body + mount)
    print(f"synced: root=<{root_name}/>, hooks rebound: {len(named)}, "
          f"{len((prelude + body + mount).encode('utf-8'))} bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
