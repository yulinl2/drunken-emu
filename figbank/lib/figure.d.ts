// Types for figure.js, so a TypeScript page (figbank/app/*) can import the bank directly.
export interface VNode { t: string; a: Record<string, unknown>; c: (VNode | string | number)[] }
export interface Report { id: string; words: number; word_budget?: number; errors: string[]; n_texts: number; texts: string[] }
export function renderFigure(spec: unknown, palette?: Record<string, string>): { node: VNode; svg: string; report: Report }
