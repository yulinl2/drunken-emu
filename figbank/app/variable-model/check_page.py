#!/usr/bin/env python3
"""check_page.py — the variable-model page's function checklist, run by a script reader in headless Chromium.

    python3 figbank/app/variable-model/check_page.py PAGE.html [--shots DIR]

The port's claim is "no loss of function" against the hand-written page it replaces. This script asserts every
function that page had, on the rendered artifact with data injected (MetaProof figures/agent-environment-demo.html):
  1 tiles: the variable count and one tile per status in the vocabulary
  2 the loop diagram (fig4 spec): every variable is a clickable item; a click selects it and the detail shows it
  3 the loss stack (fig5 spec): every functional clickable; a click fills the loss detail with its terms
  4 loss cards: click selects too
  5 search narrows the cards and dims the diagram items that no longer match
  6 the status filter narrows; the side buttons toggle (aria-pressed) and combine with the search
  7 cards: click selects; the detail carries the episode block when the variable has one
  8 the episode headline, the missing section and the footer are present
  9 dark mode: with prefers-color-scheme dark the body background changes and the diagram re-renders in the dark palette
 10 no JavaScript errors at any point
Exit 0 when everything holds; prints one JSON line with the counts it saw.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from playwright.sync_api import sync_playwright  # noqa: E402
from checks.browser import launch  # noqa: E402


def main(path, shots=None):
    src = open(path, encoding='utf-8').read()
    import re
    m = re.search(r'<script[^>]*\bid="?vars"?[^>]*>', src)
    if not m:
        print(json.dumps({'errors': ['no <script id=vars> data slot in the page']})); return 1
    data = json.loads(src[m.end():].split('</script>', 1)[0].replace('<\\/', '</'))
    n_vars, statuses = len(data['variables']), list(data['_provenance']['status_vocabulary'])
    losses = [l['id'] for l in data.get('losses', [])]
    errors, out = [], {}

    def must(cond, what):
        if not cond:
            errors.append(what)

    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={'width': 1280, 'height': 900})
        js_errors = []
        pg.on('pageerror', lambda e: js_errors.append(str(e)))
        pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())   # offline: the fallbacks must do
        pg.set_content(src, wait_until='load')
        pg.wait_for_selector('#tiles .tile')
        # 1 tiles
        tiles = pg.locator('#tiles .tile')
        must(tiles.count() == 1 + len(statuses), f'tiles: {tiles.count()} != 1 + {len(statuses)}')
        must(tiles.nth(0).locator('b').inner_text() == str(n_vars), 'first tile is not the variable count')
        # 2 loop diagram
        items = pg.locator('#diag .figure [data-id][role="button"]')
        ids = set(items.evaluate_all('els => els.map(e => e.dataset.id)'))
        var_ids = {r['id'] for r in data['variables']}
        must(var_ids <= ids, f'diagram lacks {sorted(var_ids - ids)[:5]}')
        out['diagram_items'] = len(ids)
        first = data['variables'][0]
        pg.locator(f'#diag .figure [data-id="{first["id"]}"][role="button"]').first.click()
        must(first['name'] in pg.locator('#detail').inner_text(), 'detail did not show the clicked diagram item')
        must(pg.locator(f'#diag .figure .on[data-id="{first["id"]}"]').count() == 1, 'diagram item not marked selected')
        if shots:
            pg.screenshot(path=os.path.join(shots, 'page-light.png'), full_page=True)
        # 3 loss stack
        if losses:
            fx = pg.locator('#lossdiag .figure .functional[data-id]')
            must(set(fx.evaluate_all('els => els.map(e => e.dataset.id)')) == set(losses), 'loss diagram functionals differ from losses')
            pg.locator(f'#lossdiag .figure .functional[data-id="{losses[1]}"]').click()
            lt = pg.locator('#lossdetail').inner_text()
            must(data['losses'][1]['name'] in lt and data['losses'][1]['terms'][0][:20] in lt, 'loss detail did not fill from the diagram')
            # 4 loss cards
            pg.locator(f'#losslist .card[data-loss="{losses[-1]}"]').click()
            must(data['losses'][-1]['name'] in pg.locator('#lossdetail').inner_text(), 'loss card click did not select')
        # 5 search
        total_cards = pg.locator('#list .card').count()
        must(total_cards == n_vars, f'cards: {total_cards} != {n_vars}')
        pg.fill('#q', 'cutwidth')
        narrowed = pg.locator('#list .card').count()
        must(0 < narrowed < total_cards, f'search did not narrow ({narrowed})')
        dim = pg.locator('#diag .figure .dim[data-id]').count()
        must(dim == n_vars - narrowed, f'dimmed diagram items {dim} != {n_vars - narrowed}')
        pg.fill('#q', '')
        # 6 status filter + side buttons
        pg.select_option('#st', statuses[0])
        by_status = pg.locator('#list .card').count()
        must(by_status == sum(1 for r in data['variables'] if r['status'] == statuses[0]), 'status filter count wrong')
        pg.select_option('#st', '')
        btn = pg.locator('#sides .sidebtn').first
        btn.click()
        must(btn.get_attribute('aria-pressed') == 'true', 'side button not pressed')
        side_n = pg.locator('#list .card').count()
        must(side_n == sum(1 for r in data['variables'] if r['side'] == 'environment'), 'side filter count wrong')
        pg.fill('#q', 'oracle')
        must(pg.locator('#list .card').count() < side_n, 'search does not combine with the side filter')
        pg.fill('#q', '')
        btn.click()
        must(btn.get_attribute('aria-pressed') == 'false' and pg.locator('#list .card').count() == total_cards, 'side toggle off failed')
        # 7 cards + episode block
        with_ep = next((r for r in data['variables'] if r.get('episode')), None)
        if with_ep:
            pg.locator(f'#list .card[data-id="{with_ep["id"]}"]').click()
            dt = pg.locator('#detail').inner_text()
            must('In the T0 episode' in dt and with_ep['episode']['value'][:15] in dt, 'episode block missing from the detail')
        # 8 static sections
        must(pg.locator('#episode-line').count() == (1 if data.get('_episode') else 0), 'episode line presence')
        must('What is still missing' in pg.locator('section.missing').inner_text(), 'missing section')
        must('bin/variables.py' in pg.locator('footer').inner_text(), 'footer')
        # 9 dark mode
        light_bg = pg.evaluate('getComputedStyle(document.body).backgroundColor')
        light_fill = pg.locator('#diag .figure svg > rect').first.get_attribute('fill')
        pg.emulate_media(color_scheme='dark')
        pg.wait_for_timeout(100)
        dark_bg = pg.evaluate('getComputedStyle(document.body).backgroundColor')
        dark_fill = pg.locator('#diag .figure svg > rect').first.get_attribute('fill')
        must(light_bg != dark_bg, 'body background did not change in dark mode')
        must(light_fill != dark_fill, 'diagram did not re-render with the dark palette')
        if shots:
            pg.screenshot(path=os.path.join(shots, 'page-dark.png'), full_page=True)
        # 10
        must(not js_errors, 'JS errors: ' + ' | '.join(js_errors)[:300])
        b.close()
    out.update(variables=n_vars, cards=total_cards, losses=len(losses), errors=errors)
    print(json.dumps(out, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    shots = a[a.index('--shots') + 1] if '--shots' in a else None
    if shots:
        os.makedirs(shots, exist_ok=True)
    sys.exit(main(a[0], shots))
