"""Shared readiness for artifact mounts and ordinary document bodies.

Keep the existing element/shadow-root predicate for React and custom mounts.
A plain document body can instead contain only nonempty text.
"""

READY_JS = """s => {
  const el = document.querySelector(s);
  return !!el && (el.children.length > 0 || !!el.shadowRoot ||
    (el === document.body && !!el.innerText.trim()));
}"""
