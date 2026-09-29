"""checks/affordances.py — what a reader could act on, extracted from the rendered page (never from source).

AFF_JS returns, for every element that is at least partly inside the viewport and looks operable:
  {text, x, y, w, h, salience, via, tag}
  x, y, w, h  the VISIBLE part of the element (clipped to the viewport): the centre is always a point a tap can hit,
              and a half-hidden element is as loud as the half that shows
  via = "semantic"     button / a / input / select / textarea / summary / [data-term] / an interactive ARIA role (button, link, checkbox, switch,
                       tab, menuitem*, option, radio, slider, spinbutton, textbox, combobox, searchbox, treeitem)
        "pointer-only" cursor:pointer with none of the above (on it or an ancestor): findable by eye, invisible to keyboard and screen reader
  salience = visible area × 1.5 if animated else visible area   (big loud things first; the impairment model's ordering)
Shared by explore_step.py (session-as-decider) and explore_run.py (scripted decider, sweeps).
"""
AFF_JS = r"""()=>{
  const ROLES='link,checkbox,switch,tab,menuitem,menuitemcheckbox,menuitemradio,option,radio,slider,spinbutton,textbox,combobox,searchbox,treeitem'.split(',').map(r=>`[role=${r}]`).join(',');
  const SEM='button,a,[role=button],input,select,textarea,summary,[data-term],'+ROLES;
  const sem=new Set(document.querySelectorAll(SEM));
  // a reader also finds things that merely LOOK clickable (cursor:pointer): keep the outermost such element with no semantic ancestor
  const ptr=[...document.querySelectorAll('body *')].filter(e=>!sem.has(e)&&getComputedStyle(e).cursor==='pointer'&&!e.closest(SEM)
               &&!(e.parentElement&&getComputedStyle(e.parentElement).cursor==='pointer'));
  const cand=[...sem,...ptr];
  const vp={w:innerWidth,h:innerHeight};
  return cand.map(e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e);
    const x0=Math.max(r.left,0), x1=Math.min(r.right,vp.w), y0=Math.max(r.top,0), y1=Math.min(r.bottom,vp.h);
    if(!(x1>x0&&y1>y0)||cs.visibility==='hidden') return null;
    const area=(x1-x0)*(y1-y0);
    const motion=(cs.animationName!=='none'||cs.transitionDuration!=='0s')?1.5:1;
    return {text:(e.getAttribute('aria-label')||e.textContent||e.value||e.placeholder||'').trim().replace(/\s+/g,' ').slice(0,48),
            via:sem.has(e)?'semantic':'pointer-only', tag:e.tagName.toLowerCase(),
            x:Math.round((x0+x1)/2), y:Math.round((y0+y1)/2), w:Math.round(x1-x0), h:Math.round(y1-y0),
            salience:Math.round(area*motion)};
  }).filter(Boolean);
}"""


async def settle(page, timeout_ms=5000):
    """Best-effort wait for network idle. A page that fetches its data is not ready at DOMContentLoaded (P-0a86), but one that polls or
    streams never reaches idle: so the wait is bounded, and a timeout is not an error (the session can still step, and use `wait`)."""
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass
