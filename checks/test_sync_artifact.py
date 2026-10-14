"""checks/test_sync_artifact.py -- must-fire / must-hold tests for the import handling of bin/sync_artifact.py.

An `import` statement may span lines, carry a default beside the braces, or have no clause at all (`import "x"`).
The dependency guard, the re-binding of named react imports and the stripping must all see the same statements.
Found by running the script on six inputs (2026-10-14): a multi-line import of any module, react included, left its
tail in app.jsx, which Babel cannot parse, while exit 0 said "synced"; a side-effect import was dropped unchecked.
The last tests pin what the text match does NOT see (the limits the docs list), so the docs cannot drift from the code.
No browser, under 2 s:

    python3 -m pytest -q checks/test_sync_artifact.py
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

SYNC = Path(__file__).resolve().parent.parent / "bin" / "sync_artifact.py"
APP = "export default function App() { return <div>hi</div>; }"

def sync(tmp_path, head, body=APP):
    src, out = tmp_path / "in.jsx", tmp_path / "out.jsx"
    src.write_text(head + "\n" + body + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SYNC), str(src), str(out)], capture_output=True, text=True)
    return r.returncode, r.stdout, (out.read_text(encoding="utf-8") if out.exists() else "")

def test_react_only_is_synced(tmp_path):
    rc, _, out = sync(tmp_path, 'import React from "react";')
    assert rc == 0 and "import" not in out and "ReactDOM.createRoot" in out

def test_single_line_unsupported_import_exits_2_with_the_list(tmp_path):
    rc, so, out = sync(tmp_path, 'import { LineChart } from "recharts";')
    assert rc == 2 and "UNSUPPORTED_IMPORTS: recharts" in so and out == ""

def test_single_quoted_default_import_exits_2(tmp_path):
    rc, so, _ = sync(tmp_path, "import _ from 'lodash';")
    assert rc == 2 and "UNSUPPORTED_IMPORTS: lodash" in so

def test_multi_line_unsupported_import_exits_2_with_the_list(tmp_path):
    rc, so, out = sync(tmp_path, 'import {\n  LineChart,\n  Line\n} from "recharts";')
    assert rc == 2 and "UNSUPPORTED_IMPORTS: recharts" in so and out == ""

def test_side_effect_import_of_an_unsupported_module_exits_2(tmp_path):
    rc, so, _ = sync(tmp_path, 'import "some-unsupported-pkg";')
    assert rc == 2 and "UNSUPPORTED_IMPORTS: some-unsupported-pkg" in so

def test_a_supported_import_beside_an_unsupported_one_lists_only_the_unsupported(tmp_path):
    rc, so, _ = sync(tmp_path, 'import React from "react";\nimport { Line } from "recharts";')
    assert rc == 2 and "UNSUPPORTED_IMPORTS: recharts" in so and "react," not in so

def test_multi_line_react_import_leaves_no_tail_and_rebinds_its_names(tmp_path):
    rc, _, out = sync(tmp_path, 'import React, {\n  useState,\n  useEffect\n} from "react";')
    assert rc == 0 and 'from "react"' not in out and "const {useEffect, useState} = React;" in out
    assert not [ln for ln in out.split("\n") if ln.strip() in ("useState,", "useEffect", "}")]

def test_default_beside_named_react_imports_rebinds_names_that_are_not_hooks(tmp_path):
    rc, _, out = sync(tmp_path, 'import React, { memo, forwardRef } from "react";')
    assert rc == 0 and "const {forwardRef, memo} = React;" in out

def test_hooks_used_without_an_import_are_still_rebound(tmp_path):
    rc, _, out = sync(tmp_path, "", "export default function App() { const [a] = useState(0); return <div>{a}</div>; }")
    assert rc == 0 and "const {useState} = React;" in out

def test_lines_below_a_multi_line_import_keep_their_numbers(tmp_path):
    head = 'import React, {\n  useState,\n  useEffect\n} from "react";'
    rc, _, out = sync(tmp_path, head)
    src_at = (head + "\n" + APP).split("\n").index(APP)
    out_at = out.split("\n").index(APP.replace("export default ", ""))
    assert rc == 0 and out_at == src_at + 1        # the one-line prelude is the only shift

def test_an_import_with_a_comment_between_from_and_the_module_is_still_stripped(tmp_path):
    rc, _, out = sync(tmp_path, 'import React from /* harness global */ "react";')
    assert rc == 0 and not [ln for ln in out.split("\n") if ln.startswith("import")]

def test_an_import_with_a_quote_inside_a_comment_in_its_clause_is_still_stripped(tmp_path):
    rc, _, out = sync(tmp_path, "import React, /* don't */ { useState } from \"react\";")
    assert rc == 0 and not [ln for ln in out.split("\n") if ln.startswith("import")]


# --- what the text match does NOT see, pinned so that the docstring of sync_artifact.py and the README cannot drift from
# the code. Measured 2026-10-14 against the old script too: none of these is new. Each exits 0 with an unsupported package.
UNSEEN = {
    "a comment between from and the module": 'import { Line } from /* c */ "recharts";',
    "a line comment, the module on the next line": 'import { Line } from // c\n"recharts";',
    "an indented import": '  import { Line } from "recharts";',
    "a dynamic import()": 'const L = import("recharts");',
    "export ... from": 'export { Line } from "recharts";',
}

@pytest.mark.parametrize("head", list(UNSEEN.values()), ids=list(UNSEEN))
def test_forms_the_text_match_does_not_see_pass_with_exit_0(tmp_path, head):
    rc, so, _ = sync(tmp_path, head)
    assert rc == 0 and "UNSUPPORTED_IMPORTS" not in so

def test_import_like_text_starting_a_line_in_a_comment_or_a_template_is_refused(tmp_path):
    for head in ('/*\nimport { Line } from "recharts";\n*/', 'const s = `\nimport x from "recharts"\n`;'):
        rc, so, out = sync(tmp_path, head)
        assert rc == 2 and "UNSUPPORTED_IMPORTS: recharts" in so and out == ""

def test_react_import_text_inside_a_template_is_stripped_from_the_copy(tmp_path):
    rc, _, out = sync(tmp_path, 'const s = `\nimport React from "react"\n`;')
    assert rc == 0 and "import React" not in out

def test_an_aliased_react_import_is_emitted_as_an_invalid_destructure(tmp_path):
    rc, _, out = sync(tmp_path, 'import { useState as us } from "react";')
    assert rc == 0 and re.search(r"const \{[^}]*useState as us[^}]*\} = React;", out)       # a syntax error in the browser

def test_a_namespace_react_import_leaves_the_name_unbound(tmp_path):
    rc, _, out = sync(tmp_path, 'import * as R from "react";', "export default function App() { return <div>{R.version}</div>; }")
    assert rc == 0 and "R.version" in out and not re.search(r"\b(const|let|var)\s+R\b", out)
