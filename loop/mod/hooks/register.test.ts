import { expect, mock, test } from 'claude-code/testing'

// loop (mod): the tools `compact` and `clear` take their argument from the event itself. A tool's own arguments sit beside the
// reserved keys `tool`, `tool_use_id` and `consent` (ToolCallInput, ToolCallReserved in the engine's types: "the tool's arguments
// spread beside them (`e.command` for Bash)"); there is no `e.input`. A handler that reads `e.input` sees none of them.
// INVARIANT: a tool called with its argument queues exactly what it was given.
// FAILS WHEN: `clear` called with `resume` answers "not queued", or `compact` called with `also_keep` queues without it.

const HOME = '/home/tester'
const DIR = HOME + '/.claude/loop'
const PROMPT = 'Read /tmp/state.md first, then go on.'
const STATE = '/tmp/state.md'

// The world beneath the mod: a folder in memory, the environment, and a clock that moves only when the test moves it.
function world(on: any) {
  const files = new Map<string, string>()
  const ran: Array<{ command: string; args: string }> = []
  const submitted: string[] = []
  mock.env(on, { HOME })
  const clock = mock.clock(on)
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('tool.register', (_: any, e: any) => ({ value: { tool: e.name } }))
  on('fs.exists', (_: any, e: any) => ({ value: files.has(e.path) }))
  on('fs.read', (_: any, e: any) => ({ value: files.get(e.path) ?? '' }))
  on('fs.write', (_: any, e: any) => { files.set(e.path, e.text); return { value: undefined } })
  on('session.usage', () => ({ value: { context: { tokens: 1000 }, cost: { usd: 0.5 }, rateLimits: [] } }))
  on('command.run', (_: any, e: any) => { ran.push({ command: e.command, args: e.args }); return { value: undefined } })
  on('prompt.submit', (_: any, e: any) => { submitted.push(e.text); return { text: e.text } })   // an event: it answers by its own result
  const log = () => (files.get(DIR + '/log.jsonl') ?? '').split('\n').filter(Boolean).map(l => JSON.parse(l))
  return { files, ran, submitted, clock, log }
}

test('clear called with resume queues that prompt', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const out: any = await $.tool.call({ tool: 'mcp__loop__clear', resume: PROMPT })

  expect(out.result).toContain('queued: /clear runs once this turn has ended')
  expect(out.result).toContain(PROMPT)
  expect(w.files.get(DIR + '/resume.txt')).toBe(PROMPT)         // kept, in case the clear tears the module down

  await w.clock.advance(1500)                                    // the timer: the clear runs, then the prompt is submitted
  expect(w.ran).toEqual([{ command: 'clear', args: '' }])
  expect(w.submitted).toEqual([PROMPT])
  expect(w.log().map((r: any) => r.ev)).toContain('cleared')
})

test('clear called with no resume is not queued', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const out: any = await $.tool.call({ tool: 'mcp__loop__clear' })

  expect(out.result).toContain('not queued: a clear with no resume prompt')
  await w.clock.advance(1500)
  expect(w.ran).toEqual([])
})

test('compact called with also_keep queues it as the line to keep', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const out: any = await $.tool.call({ tool: 'mcp__loop__compact', also_keep: STATE })

  expect(out.result).toContain('queued: /compact runs once this turn has ended')
  expect(out.result).toContain('also keep: ' + STATE)

  await w.clock.advance(1500)                                    // the timer: the compaction is started with that line
  expect(w.ran).toEqual([{ command: 'compact', args: 'also keep: ' + STATE }])
  expect(w.log().map((r: any) => r.ev)).toContain('ran')
})
