#!/usr/bin/env node
// figbank/render_svg.js — spec.json → figure.svg, with the assembler's report on stderr.
//
//   node figbank/render_svg.js SPEC.json OUT.svg [--report OUT.json] [--lenient]
//
// Exit 0 when the figure has no errors; exit 3 when it has (overflow, word budget, forbidden
// string, truncation) — the SVG is still written so the maker can look at it. --lenient writes
// and exits 0 regardless (for drafting only; the pipeline never passes it).

import { readFileSync, writeFileSync } from 'node:fs';
import { renderFigure } from './lib/figure.js';

const args = process.argv.slice(2);
const reportIdx = args.indexOf('--report');
const reportPath = reportIdx >= 0 ? args[reportIdx + 1] : null;
const [specPath, outPath] = args.filter((a, i) => !a.startsWith('--') && !(reportIdx >= 0 && i === reportIdx + 1));
if (!specPath || !outPath) { console.error('usage: render_svg.js SPEC.json OUT.svg [--report OUT.json] [--lenient]'); process.exit(64); }

const spec = JSON.parse(readFileSync(specPath, 'utf8'));
const { svg, report } = renderFigure(spec);
writeFileSync(outPath, svg + '\n');
if (reportPath) writeFileSync(reportPath, JSON.stringify(report, null, 1) + '\n');
console.error(`${spec.id}: ${report.words} words of running text (budget ${report.word_budget ?? 'none'}), ${report.n_texts} text runs, ${report.errors.length} errors`);
for (const e of report.errors) console.error('  ' + e);
process.exit(report.errors.length && !args.includes('--lenient') ? 3 : 0);
