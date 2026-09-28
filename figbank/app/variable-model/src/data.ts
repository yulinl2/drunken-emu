// src/data.ts — the page's data contract with MetaProof's model/variables.json (+ what bin/variables.py adds).

export type Status = 'defined' | 'estimated' | 'measured' | 'spec' | 'implemented'
export type Side = 'environment' | 'agent' | 'interface' | 'objective' | 'dynamics' | 'meta'

export interface Episode { value: string; role: string; knockout?: string | null; hierarchical?: string; flat?: string; watch: string }
export interface Variable {
  id: string; symbol: string; name: string; side: Side; rl: string; gloss: string; defined_in: string; status: Status; measured_by: string
  episode?: Episode
}
export interface Loss {
  id: string; name: string; grain: string; formula: string; terms: string[]; constraint: string; status: Status; where: string
  prices: string | null; relation: string; episode?: string; short: string; limits?: string[]
}
export interface Provenance {
  version: string; status_vocabulary: Record<string, string>; sides: Record<Side, string>; loss_reading?: string; role?: string
}
export interface EpisodeHeadline {
  seeds: number[]
  hierarchical: { final_uncovered: number; drops_total: number; accepted: number }
  flat: { final_uncovered: number; drops_total: number; accepted: number }
  front: { hierarchical: number; flat: number }
}
export interface Data {
  _provenance: Provenance
  variables: Variable[]
  losses?: Loss[]
  _episode?: EpisodeHeadline
  _specs?: Record<string, unknown>   // figure specs (drunken-emu figbank schema), keyed by figure id
}

export const SIDES: Side[] = ['environment', 'agent', 'interface', 'objective', 'dynamics', 'meta']
export const SIDE_TITLE: Record<Side, string> = { environment: 'Environment', agent: 'Agent', interface: 'Interface', objective: 'Objective', dynamics: 'Dynamics', meta: 'Meta' }
export const SIDE_VAR: Record<Side, string> = { environment: 'var(--env)', agent: 'var(--agent)', interface: 'var(--iface)', objective: 'var(--obj)', dynamics: 'var(--dyn)', meta: 'var(--meta)' }
export const LOSS_VAR: Record<string, string> = { J: 'var(--obj)', gaps: 'var(--obj)', decoder_load: 'var(--dyn)', tree_score: 'var(--agent)', corpus: 'var(--meta)' }

export function loadData(): Data | null {
  const el = document.getElementById('vars')
  const txt = el?.textContent?.trim() ?? ''
  if (!txt || txt === '__JSON__') return null
  try { return JSON.parse(txt) as Data } catch { return null }
}
