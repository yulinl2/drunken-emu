import { useState } from "react";
// Fixture for checks/fragment_links.py: one live fragment link, one planted dead one (#nowhere),
// one target inside a closed <details> (Chromium's fragment navigation OPENS the details, so this
// one is live -- measured 2026-09-26, kept here as the regression for that fact), and one target
// with display:none (fragment navigation does not undo that). Expected verdict: FAIL with
// dead=['#nowhere'], hidden=['#unshown'].
export default function Fixture() {
  const [n, setN] = useState(0);
  return (
    <div className="p-4">
      <nav className="flex gap-3">
        <a href="#live">Live</a>
        <a href="#nowhere">Dead</a>
        <a href="#folded">Folded</a>
        <a href="#unshown">Unshown</a>
      </nav>
      <section id="live" className="mt-6">
        <button onClick={() => setN(n + 1)} style={{ minHeight: 40 }}>count {n}</button>
      </section>
      <details className="mt-6">
        <summary>closed on load</summary>
        <p id="folded">a target that stays hidden unless the details opens</p>
      </details>
      <p id="unshown" style={{ display: "none" }}>a target that display:none keeps hidden</p>
    </div>
  );
}
