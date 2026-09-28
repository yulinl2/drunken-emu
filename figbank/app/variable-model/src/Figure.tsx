// src/Figure.tsx — a bank figure spec, rendered by the same code as the LaTeX SVG, made interactive.
//
// renderFigure() gives a vnode tree; before handing it to React we mark the selected and the filtered-out
// items (class "on" / "dim") and make every [data-id] group focusable. Clicks and keys are delegated from the
// wrapper, so the bank's components stay host-agnostic.

import React, { useMemo } from 'react'
import { renderFigure } from '../../../lib/figure.js'
import type { VNode } from '../../../lib/figure.js'
import { toReact } from '../../../lib/vnode.js'
import { LIGHT, DARK } from '../../../lib/palette.js'

interface Props {
  spec: unknown
  dark: boolean
  selected?: string | null
  dimmed?: (id: string) => boolean
  onPick: (id: string) => void
  label: string
}

function decorate(node: VNode | string | number, selected: string | null | undefined, dimmed?: (id: string) => boolean): VNode | string | number {
  if (typeof node !== 'object') return node
  const a = { ...node.a }
  const id = a['data-id'] as string | undefined
  if (id && ['item', 'chip', 'functional', 'region'].includes(String(a.class))) {
    const cls = [a.class, id === selected ? 'on' : '', dimmed && dimmed(id) ? 'dim' : ''].filter(Boolean).join(' ')
    a.class = cls
    if (!cls.includes('region')) { a.tabindex = 0; a.role = 'button'; a['aria-label'] = id }
  }
  return { t: node.t, a, c: node.c.map((ch: VNode | string | number) => decorate(ch, selected, dimmed)) }
}

export default function Figure({ spec, dark, selected, dimmed, onPick, label }: Props) {
  const tree = useMemo(() => {
    const { node, report } = renderFigure(spec, dark ? DARK : LIGHT)
    if (report.errors.length) console.warn('figure', report.id, report.errors)
    return node
  }, [spec, dark])
  const element = useMemo(() => toReact(React, decorate(tree, selected, dimmed)) as React.ReactElement, [tree, selected, dimmed])
  const pick = (target: EventTarget | null) => {
    const g = (target as Element | null)?.closest?.('[data-id]') as (Element & { dataset: DOMStringMap }) | null
    if (g?.dataset.id && !g.classList.contains('region')) onPick(g.dataset.id)
  }
  return (
    <div className="figure" role="img" aria-label={label}
      onClick={e => pick(e.target)}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(e.target) } }}>
      {element}
    </div>
  )
}
