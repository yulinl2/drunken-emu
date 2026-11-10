import type { Register } from 'claude-code'

// loop (mod): the two things a session cannot do from a shell. It reads its own usage, and it compacts itself.
// INVARIANT: every compaction of this conversation (typed, automatic or started by the tool) carries the principal's line and the
//   session's also-keep text, and leaves one log row with the tokens and the cost before and after.
// FAILS WHEN: line.txt exists and a compaction's summary request does not hold it; or `compact` answers "queued" and no row
//   `ran` or `refused` follows in the log.
// Observed 2026-11-10 in a cloud session, engine 2.1.321: $.command.run({ command: 'compact' }) starts a compaction once the turn has
// ended. $.session.compact is refused there in the engine's words: "not available in a headless (-p / SDK) session yet". Not observed:
// a terminal session, where the second way below is the documented one.
// The mod decides nothing: the model calls the tools. State is three files in ~/.claude/loop/, which the project's install writes:
//   line.txt        the principal's standing line for every compaction (the project's own words; none here)
//   also-keep.txt   what else this session must carry over; the session keeps it current
//   log.jsonl       one row per turn, per compaction and per answer of the engine

const VERSION = '0.2.0'
const said = (err: unknown): string => String((err as any)?.message ?? err).slice(0, 400)

async function dir($: any): Promise<string> {
  return ((await $.env.get('HOME')) || '/root') + '/.claude/loop'
}

async function text($: any, name: string): Promise<string> {
  try {
    const path = (await dir($)) + '/' + name
    return (await $.fs.exists(path)) ? String(await $.fs.read(path)).trim() : ''
  } catch { return '' }
}

async function reading($: any): Promise<Record<string, unknown>> {
  try {
    const u: any = await $.session.usage()
    return { tokens: u?.context?.tokens ?? null, usd: u?.cost?.usd ?? null, limits: (u?.rateLimits ?? []).map((w: any) => [w.kind, w.percentUsed]) }
  } catch (err) { return { usage_error: said(err) } }
}

let chain: Promise<void> = Promise.resolve()
function note($: any, row: Record<string, unknown>): Promise<void> {
  const at = new Date().toISOString()
  chain = chain.then(async () => {
    try {
      const path = (await dir($)) + '/log.jsonl'
      const old = (await $.fs.exists(path)) ? await $.fs.read(path) : ''
      await $.fs.write(path, old + JSON.stringify({ at, v: VERSION, ...row }) + '\n')
    } catch { /* the log is best effort: a full disk must not break a turn */ }
  })
  return chain
}

// What a compaction is told to keep, each part once: what was typed, the principal's line, the also-keep text, what the call adds.
async function keep($: any, typed: string, extra: string): Promise<string> {
  const parts = [typed.trim()]
  const more: Array<[string, string]> = [['', await text($, 'line.txt')], ['also keep: ', await text($, 'also-keep.txt')], ['also keep: ', extra.trim()]]
  for (const [label, t] of more) if (t && !parts.join('\n').toLowerCase().includes(t.toLowerCase())) parts.push(label + t)
  return parts.filter(Boolean).join('; ')
}

let pending = false
function start($: any, args: string): void {
  if (pending) return
  pending = true
  $.clock.after(1500, async () => {
    try {
      const ways: Array<[string, () => Promise<unknown>]> = [
        ['command.run', () => $.command.run({ command: 'compact', args })],
        ['session.compact', () => $.session.compact({ instructions: args })],
      ]
      for (const [way, run] of ways) {
        try { await run(); await note($, { ev: 'ran', way }); return }
        catch (err) { await note($, { ev: 'refused', way, error: said(err) }) }
      }
    } finally { pending = false }
  })
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.tool.register({
      name: 'usage',
      description:
        "Reads this session's own usage now, without a person: the context window's fill, each rate-limit window with the percent used and its reset time, and the session's cost. Call it before long work and when deciding whether to compact.",
      inputSchema: { type: 'object', properties: {} },
      isDeferred: false,
    })
    await $.tool.register({
      name: 'compact',
      description:
        "Compacts this conversation once this turn has ended, as if the person typed /compact with the principal's standing line. First write what else must survive (the state file's path, open work) into ~/.claude/loop/also-keep.txt, or pass it as also_keep. Call it at a boundary of the work, not in the middle of a step; ~/.claude/loop/log.jsonl then holds what the engine answered.",
      inputSchema: { type: 'object', properties: { also_keep: { type: 'string' } } },
      isDeferred: false,
    })
    return next(e)
  })

  on('tool.call', { tool: /^mcp__loop__usage$/ }, async $ => {
    try {
      const u: any = await $.session.usage()
      return { result: JSON.stringify({ context: u.context, rateLimits: u.rateLimits, cost: u.cost, startedAt: u.startedAt }) }
    } catch (err) { return { result: 'usage unavailable: ' + said(err) } }
  })

  on('tool.call', { tool: /^mcp__loop__compact$/ }, async ($, e) => {
    if (pending) return { result: 'already queued: it runs when the session is idle' }
    const args = await keep($, '', String(((e as any).input ?? {}).also_keep ?? ''))
    await note($, { ev: 'queued', args_len: args.length, ...(await reading($)) })
    start($, args)
    return { result: 'queued: /compact runs once this turn has ended, with: ' + args.slice(0, 400) }
  })

  on('turn.complete', async ($, e, next) => {
    void note($, { ev: 'turn', ...(await reading($)) })
    return next(e)
  })

  on('session.compact', async ($, e, next) => {
    const ev: any = e
    if (ev.agentId) return next(e)   // a subagent's compaction is not this conversation's
    let merged: string | undefined = ev.instructions
    try { merged = await keep($, typeof ev.instructions === 'string' ? ev.instructions : '', '') }
    catch (err) { await note($, { ev: 'hook_error', error: said(err) }) }
    const before = await reading($)
    const res: any = await next({ ...e, instructions: merged } as any)
    await note($, { ev: 'compacted', trigger: ev.trigger ?? null, skip: res?.skip ?? null, tokens_before: res?.tokensBefore ?? null, tokens_after: res?.tokensAfter ?? null, usd_before: before.usd ?? null, ...(await reading($)) })
    return res
  })
}
