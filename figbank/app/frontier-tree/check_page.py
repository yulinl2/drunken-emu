#!/usr/bin/env python3
"""check_page.py — the tree page's function checklist, run by a script reader in headless Chromium.

    python3 figbank/app/frontier-tree/check_page.py PAGE.html [--shots DIR]

Asserts:
  1 tiles: the node count and one tile per status present in the data
  2 the diagram: every tree node is a clickable, focusable [data-id]; a click selects it and the detail
    panel shows its label and its first detail row's value
  3 cards: the card list matches the node count 1:1; a card click selects too, same as a diagram click
  4 search narrows the card list and dims the diagram nodes that no longer match
  5 the status filter narrows the card list
  6 dark mode: body background changes and the diagram re-renders in the dark palette
  7 no JavaScript errors at any point
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
    nodes = data['nodes']
    statuses = sorted({n['status'] for n in nodes})
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
        must(tiles.nth(0).locator('b').inner_text() == str(len(nodes)), 'first tile is not the node count')
        # 2 diagram
        items = pg.locator('#diag .figure [data-id][role="button"]')
        ids = set(items.evaluate_all('els => els.map(e => e.dataset.id)'))
        node_ids = {n['id'] for n in nodes}
        must(ids and ids <= node_ids, f'diagram items are not nodes: {sorted(ids - node_ids)[:5]}')
        out['diagram_items'] = len(ids)
        first = next(n for n in nodes if n['id'] in ids)
        pg.locator(f'#diag .figure [data-id="{first["id"]}"][role="button"]').first.click()
        detail = pg.locator('#detail').inner_text()
        must(first['label'] in detail, 'detail did not show the clicked diagram node\'s label')
        if first['detail']:
            must(first['detail'][0][1][:20] in detail, 'detail did not show the clicked node\'s first detail row')
        must(pg.locator(f'#diag .figure .on[data-id="{first["id"]}"]').count() == 1, 'diagram node not marked selected')
        if shots:
            pg.screenshot(path=os.path.join(shots, 'page-light.png'), full_page=True)
        # 3 cards
        total_cards = pg.locator('#list .card').count()
        must(total_cards == len(nodes), f'cards: {total_cards} != {len(nodes)}')
        other = next(n for n in nodes if n['id'] != first['id'])
        pg.locator(f'#list .card[data-id="{other["id"]}"]').click()
        must(other['label'] in pg.locator('#detail').inner_text(), 'card click did not select')
        # 4 search
        pg.fill('#q', first['id'])
        narrowed = pg.locator('#list .card').count()
        must(0 < narrowed < total_cards, f'search did not narrow ({narrowed})')
        dim = pg.locator('#diag .figure .dim[data-id]').count()
        must(dim > 0, 'search did not dim any diagram node')
        pg.fill('#q', '')
        # 5 status filter
        pg.select_option('#st', statuses[0])
        by_status = pg.locator('#list .card').count()
        must(by_status == sum(1 for n in nodes if n['status'] == statuses[0]), 'status filter count wrong')
        pg.select_option('#st', '')
        # 6 dark mode
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
        # 7
        must(not js_errors, 'JS errors: ' + ' | '.join(js_errors)[:300])
        b.close()
    out.update(nodes=len(nodes), cards=total_cards, statuses=len(statuses), errors=errors)
    print(json.dumps(out, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    shots = a[a.index('--shots') + 1] if '--shots' in a else None
    if shots:
        os.makedirs(shots, exist_ok=True)
    sys.exit(main(a[0], shots))
