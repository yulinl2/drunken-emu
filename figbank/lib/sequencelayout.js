// figbank/lib/sequencelayout.js — a sequence diagram's geometry, computed from its data, not
// hand-placed: participant column x-positions (auto-sized to each label's measured width, same
// "computed, never hand-placed" rule as boundaries/treelayout.js) and one y per message row, in
// message order (time flows downward, no explicit timestamps needed for a first version).

import { measure } from './text.js';

export function layoutSequence(participants, messages, opts = {}) {
  const { gapX = 36, minW = 90, padX = 16, px = 13, headerH = 34, rowGap = 34, marginY = 16 } = opts;
  if (!participants.length) throw new Error('layoutSequence: no participants');
  const seen = new Set();
  for (const pt of participants) {
    if (seen.has(pt.id)) throw new Error(`layoutSequence: duplicate participant id ${JSON.stringify(pt.id)}`);
    seen.add(pt.id);
  }
  const widths = {}, xById = {};
  let cursor = 0;
  for (const pt of participants) {
    const w = Math.max(minW, measure(pt.label, px, false, true) + 2 * padX);
    widths[pt.id] = w;
    xById[pt.id] = cursor + w / 2;
    cursor += w + gapX;
  }
  const totalWidth = cursor - gapX;
  const rows = messages.map((m, i) => {
    if (!(m.from in xById)) throw new Error(`layoutSequence: message ${i} references unknown participant ${JSON.stringify(m.from)}`);
    if (!(m.to in xById)) throw new Error(`layoutSequence: message ${i} references unknown participant ${JSON.stringify(m.to)}`);
    if (m.from === m.to) throw new Error(`layoutSequence: message ${i} is a self-message (${JSON.stringify(m.from)} -> itself) — not supported yet, no participant may message itself`);
    return { y: headerH + marginY + (i + 0.5) * rowGap, x1: xById[m.from], x2: xById[m.to] };
  });
  const totalHeight = headerH + marginY + messages.length * rowGap + marginY;
  return { widths, xById, rows, totalWidth, totalHeight, headerH };
}
