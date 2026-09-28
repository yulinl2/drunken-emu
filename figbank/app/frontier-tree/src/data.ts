// src/data.ts — the page's data contract. Deliberately generic (drunken-emu #12: "a new small React app
// under figbank/app/", meant to be a template for any tree, not hardcoded to one dataset): a node is an id,
// its parent, a status word (any vocabulary — figbank/lib/palette.js's statusStyle() already resolves
// several), a short label for the picture, and an ordered list of key/value pairs for the detail panel. The
// consuming repo's own script builds this from whatever source it has (MetaProof's first instance:
// ledgers/frontier.jsonl) and injects it into the __JSON__ slot; nothing here knows about frontier.jsonl.

export interface Node {
  id: string
  parent: string | null
  status: string
  label: string
  detail: Array<[string, string]>   // shown in the detail panel, in order, when this node is selected
}
export interface Provenance {
  title: string
  description: string
  status_vocabulary?: Record<string, string>
  source?: string
  generated_by?: string
}
export interface Data {
  _provenance: Provenance
  nodes: Node[]
  _spec: unknown   // the figbank tree spec used for the picture (drunken-emu figbank/schema/figure.schema.json)
}

export function loadData(): Data | null {
  const el = document.getElementById('vars')
  const txt = el?.textContent?.trim() ?? ''
  if (!txt || txt === '__JSON__') return null
  try { return JSON.parse(txt) as Data } catch { return null }
}
