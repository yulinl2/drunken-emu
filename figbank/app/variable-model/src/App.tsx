// src/App.tsx — the unified variable model, one page. Ported from MetaProof bin/variables.py's hand-written
// HTML (2026-09-28) with no loss of function; the two diagrams are now the bank's fig4 and fig5 specs rendered
// by the same code as the LaTeX figures (src/Figure.tsx), so the paper and the page cannot drift apart.

import { useEffect, useMemo, useState } from 'react'
import Figure from './Figure'
import { loadData, SIDES, SIDE_TITLE, SIDE_VAR, LOSS_VAR } from './data'
import type { Data, Loss, Variable, Side } from './data'

function useDark(): boolean {
  const get = () => {
    const forced = document.documentElement.getAttribute('data-theme')
    if (forced) return forced === 'dark'
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
  }
  const [dark, setDark] = useState(get)
  useEffect(() => {
    const mq = window.matchMedia?.('(prefers-color-scheme: dark)')
    const on = () => setDark(get())
    mq?.addEventListener?.('change', on)
    const mo = new MutationObserver(on); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => { mq?.removeEventListener?.('change', on); mo.disconnect() }
  }, [])
  return dark
}

const StatusTag = ({ s }: { s: string }) => <span className={`status s-${s}`}>{s}</span>

export default function App() {
  const data = useMemo(loadData, [])
  if (!data) return <main className="p-6"><h1>No data</h1><p className="lede">This shell has no model injected. MetaProof's <code>make variables</code> writes <code>model/variables.json</code> into it.</p></main>
  return <Page data={data} />
}

function Page({ data }: { data: Data }) {
  const dark = useDark()
  const rows = data.variables, prov = data._provenance, losses = data.losses ?? []
  const [side, setSide] = useState<Side | ''>('')
  const [status, setStatus] = useState('')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<string | null>(null)
  const [loss, setLoss] = useState<string | null>(null)

  const counts = useMemo(() => { const c: Record<string, number> = {}; rows.forEach(r => { c[r.status] = (c[r.status] || 0) + 1 }); return c }, [rows])
  const q = query.toLowerCase()
  const visible = (r: Variable) => (!side || r.side === side) && (!status || r.status === status) &&
    (!q || [r.symbol, r.name, r.rl, r.gloss, r.defined_in, r.measured_by].join(' ').toLowerCase().includes(q))
  const byId = useMemo(() => Object.fromEntries(rows.map(r => [r.id, r])), [rows])
  const lossById = useMemo(() => Object.fromEntries(losses.map(l => [l.id, l])), [losses])
  const sel = selected ? byId[selected] : null
  const selLoss = loss ? lossById[loss] : null
  const dimmed = useMemo(() => (id: string) => { const r = byId[id]; return !!r && !visible(r) }, [byId, side, status, q])  // eslint-disable-line react-hooks/exhaustive-deps

  const select = (id: string) => {
    setSelected(id)
    requestAnimationFrame(() => { const card = document.querySelector<HTMLElement>(`.card[data-id="${CSS.escape(id)}"]`); if (card && window.innerWidth > 860) card.scrollIntoView({ block: 'nearest' }) })
  }
  const e = data._episode
  const fig4 = data._specs?.['variable-map'] ?? data._specs?.['fig4-agent-environment'], fig5 = data._specs?.['fig5-loss-stack']

  return (
    <main className="py-6 pb-12" style={{ paddingInline: 'clamp(16px, 4vw, 48px)' }}>
      <header className="grid gap-2.5 mb-6">
        <h1>The unified variable model</h1>
        <p className="lede">Every variable of MetaProof's agent–environment model on one page, grouped by which side of the loop it belongs to, with its name in the agentic / reinforcement-learning vocabulary, where the model defines it, and whether it has ever been measured. Click any item in a diagram or any card; the detail panel also shows what the variable does in one worked maintenance episode on testbed T0 and what its knock-out changes. Generated from <code>model/variables.json</code> and <code>experiments/results/one-episode-T0.json</code>; the table form is <code>model/VARIABLES.md</code>; the loop diagram is the variable map (every variable in the box of its side) and the loss stack is the paper's fig. 5, both drawn from the same spec bank as the paper's figures.</p>
        {e && <div id="episode-line" className="lede" style={{ fontSize: 13.5 }}>
          <b>One episode, every variable (T0, {e.seeds.length} seeds):</b> along-order front {e.front.hierarchical} vs {e.front.flat}; uncovered defects at the end {e.hierarchical.final_uncovered} vs {e.flat.final_uncovered}; constraints dropped from the open set {e.hierarchical.drops_total} vs {e.flat.drops_total}; accepted {e.hierarchical.accepted.toFixed(2)} vs {e.flat.accepted.toFixed(2)} (hierarchical vs flat).
        </div>}
        <div id="tiles" className="flex flex-wrap gap-2.5 mt-1.5">
          <div className="tile"><b>{rows.length}</b><span>variables</span></div>
          {Object.keys(prov.status_vocabulary).map(k => <div className="tile" key={k}><b>{counts[k] || 0}</b><span>{k}</span></div>)}
        </div>
      </header>

      {fig4 ? <div className="diagram my-2.5 mb-5" id="diag">
        <Figure spec={fig4} dark={dark} selected={selected} dimmed={dimmed} onPick={select}
          label="Agent–environment loop: environment on the left, agent on the right, observation and action channels between them, objective and dynamics below, meta around." />
      </div> : null}

      {losses.length > 0 && <section className="lossstack mt-2 mb-6 border-t pt-3" style={{ borderColor: 'var(--line)' }}>
        <h2 className="mb-1.5">The loss, at four grains</h2>
        <p className="lede" id="loss-reading">{prov.loss_reading || ''}</p>
        {fig5 ? <div className="diagram my-2.5 mb-5" id="lossdiag">
          <Figure spec={fig5} dark={dark} selected={loss} onPick={id => setLoss(id)}
            label="The loss stack: J on top; the per-claim gaps and the decoder load below it; the tree score and the corpus functional at the bottom." />
        </div> : null}
        <div className="layout grid gap-5 items-start" style={{ gridTemplateColumns: 'minmax(0,1fr) 340px' }}>
          <div id="losslist" className="grid gap-2.5" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))' }}>
            {losses.map(l => <button type="button" key={l.id} className={'card' + (loss === l.id ? ' on' : '')} data-loss={l.id} style={{ ['--side' as string]: LOSS_VAR[l.id] }} onClick={() => setLoss(l.id)}>
              <span className="sym">{l.formula.length > 60 ? l.formula.slice(0, 58) + '…' : l.formula}</span><span className="nm">{l.name}</span><span className="rl">{l.grain}</span><StatusTag s={l.status} />
            </button>)}
          </div>
          <aside className="detail" id="lossdetail" aria-live="polite">
            {selLoss ? <LossDetail l={selLoss} by={lossById} /> : <><h3>Pick a functional</h3><p className="rl text-[13px]" style={{ color: 'var(--muted)' }}>Formula, terms, constraint, limits, and what instantiates it in the T0 episode.</p></>}
          </aside>
        </div>
      </section>}

      <div className="controls flex flex-wrap gap-2 items-center my-2 mb-3.5" role="group" aria-label="filters">
        <input id="q" type="search" className="field" style={{ minWidth: 220 }} placeholder="search symbol, name, RL name, gloss" aria-label="search" value={query} onChange={ev => setQuery(ev.target.value)} />
        <select id="st" className="field" aria-label="status filter" value={status} onChange={ev => setStatus(ev.target.value)}>
          <option value="">every status</option>
          {Object.entries(prov.status_vocabulary).map(([k, v]) => <option key={k} value={k}>{k} — {v}</option>)}
        </select>
        <span id="sides" className="flex flex-wrap gap-2">
          {SIDES.map(s => <button type="button" key={s} className="sidebtn" style={{ borderLeftColor: SIDE_VAR[s] }} aria-pressed={side === s} onClick={() => setSide(side === s ? '' : s)}>{SIDE_TITLE[s]}</button>)}
        </span>
      </div>

      <div className="layout grid gap-5 items-start" style={{ gridTemplateColumns: 'minmax(0,1fr) 340px' }}>
        <div id="list">
          {SIDES.map(s => {
            const items = rows.filter(r => r.side === s && visible(r)); if (!items.length) return null
            return <div key={s}>
              <div className="group mt-4 mb-2 flex items-baseline gap-2.5 flex-wrap">
                <h2 style={{ color: SIDE_VAR[s] }}>{SIDE_TITLE[s]}</h2><span className="n text-[13px]" style={{ color: 'var(--muted)' }}>{items.length} of {rows.filter(r => r.side === s).length}</span>
                <span className="desc basis-full text-[13.5px]" style={{ color: 'var(--muted)' }}>{prov.sides[s]}</span>
              </div>
              <div className="cards grid gap-2.5" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))' }}>
                {items.map(r => <button type="button" key={r.id} className={'card' + (selected === r.id ? ' on' : '')} data-id={r.id} style={{ ['--side' as string]: SIDE_VAR[s] }} onClick={() => select(r.id)}>
                  <span className="sym">{r.symbol}</span><span className="nm">{r.name}</span><span className="rl">{r.rl}</span><StatusTag s={r.status} />
                </button>)}
              </div>
            </div>
          })}
        </div>
        <aside className="detail" id="detail" aria-live="polite">
          {sel ? <VarDetail r={sel} prov={prov} /> : <><h3>Pick a variable</h3><p className="rl text-[13px]" style={{ color: 'var(--muted)' }}>The detail — symbol, gloss, where it is defined, how it is measured — appears here.</p></>}
        </aside>
      </div>

      <section className="missing mt-7 border-t pt-3.5" style={{ borderColor: 'var(--line)' }}>
        <h2>What is still missing</h2>
        <ul className="list-disc pl-5 mt-2">
          <li><b>No channel has a measured rate.</b> Bandwidth is defined as information per token of payload; the fixed cost of a spawn hop is the only channel number on record.</li>
          <li><b>The cognitive prior is two symbols, not an instrument.</b> <span className="mono">p</span> and <span className="mono">M_D</span> are defined; calibrating one instance is OP-6.</li>
          <li><b>Task-structure complexity is three quantities and one bracketed cost</b> (<span className="mono">W</span>, <span className="mono">λ₁</span>, the dependency DAG's depth and branching; <span className="mono">C*</span>), on purpose: they answer different questions.</li>
          <li><b>The policy and the action set are specified, not implemented</b> here (OP-29, MetaProof #44); the dirtree-loop harness holds the partial implementation.</li>
          <li><b>The radius is a rule without a check</b> (OP-30, MetaProof #45).</li>
        </ul>
      </section>
      <footer className="mt-7 text-[13px]" style={{ color: 'var(--muted)' }}>MetaProof · <span className="mono">model/definitions.md</span> §1–§12 · version {prov.version} · this page is regenerated by <span className="mono">bin/variables.py</span> from a React shell built in drunken-emu <span className="mono">figbank/app/variable-model</span>; a stale copy fails the local checks.</footer>
    </main>
  )
}

function VarDetail({ r, prov }: { r: Variable; prov: Data['_provenance'] }) {
  const ep = r.episode
  return <>
    <h3 style={{ color: SIDE_VAR[r.side] }}>{r.name}</h3>
    <div className="mono mt-1">{r.symbol}</div>
    <dl>
      <dt>side</dt><dd>{SIDE_TITLE[r.side]}</dd>
      <dt>RL name</dt><dd>{r.rl}</dd>
      <dt>gloss</dt><dd>{r.gloss}</dd>
      <dt>defined in</dt><dd>{r.defined_in}</dd>
      <dt>status</dt><dd><StatusTag s={r.status} /> — {prov.status_vocabulary[r.status] || ''}</dd>
      <dt>measured by</dt><dd>{r.measured_by}</dd>
    </dl>
    {ep && <>
      <h3 className="mt-3.5" style={{ fontSize: 15 }}>In the T0 episode</h3>
      <dl>
        <dt>value</dt><dd>{ep.value}</dd>
        <dt>enters</dt><dd>{ep.role}</dd>
        <dt>knock-out</dt><dd>{ep.knockout ? ep.knockout : 'none (definitional or a reading)'}</dd>
        {ep.hierarchical && <><dt>hierarchical</dt><dd className="mono text-[12px]">{ep.hierarchical}</dd><dt>flat</dt><dd className="mono text-[12px]">{ep.flat}</dd></>}
        <dt>watch</dt><dd>{ep.watch}</dd>
      </dl>
    </>}
  </>
}

function LossDetail({ l, by }: { l: Loss; by: Record<string, Loss> }) {
  return <>
    <h3 style={{ color: LOSS_VAR[l.id] }}>{l.name}</h3>
    <div className="mono mt-1.5 text-[12.5px]">{l.formula}</div>
    <dl>
      <dt>grain</dt><dd>{l.grain}</dd>
      <dt>terms</dt><dd>{l.terms.map((t, i) => <div key={i}>· {t}</div>)}</dd>
      <dt>constraint</dt><dd>{l.constraint}</dd>
      <dt>prices</dt><dd>{l.prices ? by[l.prices]?.name : '—'}</dd>
      <dt>relation</dt><dd>{l.relation}</dd>
      {l.limits && <><dt>limits</dt><dd>{l.limits.map((t, i) => <div key={i}>· {t}</div>)}</dd></>}
      <dt>status</dt><dd><StatusTag s={l.status} /></dd>
      <dt>where</dt><dd>{l.where}</dd>
      <dt>in the T0 episode</dt><dd>{l.episode || '—'}</dd>
    </dl>
  </>
}
