import type { VNode } from './figure.js'
export function h(t: string, a?: Record<string, unknown>, ...c: unknown[]): VNode
export function esc(s: unknown): string
export function toSvg(node: VNode | string | number, indent?: string): string
export function toReact(React: unknown, node: VNode | string | number, key?: string | number): unknown
export function texts(node: VNode | string | number, out?: string[]): string[]
