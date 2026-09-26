import { useState } from "react";
// Clean fixture for checks/fragment_links.py (the PASS path): a plain link, a percent-encoded
// fragment whose id contains a space (the browser decodes #section%202 to "section 2"), and an id
// containing a double quote (must not break selection -- anchors are selected by handle, not CSS).
// Expected verdict: PASS with three anchors checked.
export default function Clean() {
  const [n, setN] = useState(0);
  return (
    <div className="p-4">
      <nav className="flex gap-3">
        <a href="#plain">Plain</a>
        <a href="#section%202">Encoded</a>
        <a href={'#say-"hi"'}>Quoted</a>
      </nav>
      <section id="plain" className="mt-6"><button onClick={() => setN(n + 1)} style={{ minHeight: 40 }}>count {n}</button></section>
      <section id="section 2" className="mt-6"><p>percent-encoded target</p></section>
      <section id={'say-"hi"'} className="mt-6"><p>quoted target</p></section>
    </div>
  );
}
