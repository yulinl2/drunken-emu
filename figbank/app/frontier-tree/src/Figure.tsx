// src/Figure.tsx — a bank tree spec, rendered by the same code as the static SVG, made interactive.
// Same shape as figbank/app/variable-model/src/Figure.tsx, with one difference: the pickable class list
// includes 'treenode' (variable-model's diagrams have no trees, so its copy doesn't need to).

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

const PICKABLE = ['item', 'chip', 'functional', 'treenode']

function decorate(node: VNode | string | number, selected: string | null | undefined, dimmed?: (id: string) => boolean): VNode | string | number {
  if (typeof node !== 'object') return node
  const a = { ...node.a }
  const id = a['data-id'] as string | undefined
  if (id && PICKABLE.includes(String(a.class))) {
    const cls = [a.class, id === selected ? 'on' : '', dimmed && dimmed(id) ? 'dim' : ''].filter(Boolean).join(' ')
    a.class = cls
    a.tabindex = 0; a.role = 'button'; a['aria-label'] = id
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
    const g = (target as Element | null)?.closest?.('[role="button"][data-id]') as (Element & { dataset: DOMStringMap }) | null
    if (g?.dataset.id && PICKABLE.some(c => g.classList.contains(c))) onPick(g.dataset.id)
  }
  return (
    <div className="figure" role="img" aria-label={label}
      onClick={e => pick(e.target)}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(e.target) } }}>
      {element}
    </div>
  )
}
