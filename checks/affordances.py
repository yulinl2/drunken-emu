"""checks/affordances.py — what a reader could act on, extracted from the rendered page (never from source).

AFF_JS returns, for every element visible in the viewport that looks operable:
  {text, x, y, w, h, salience, via, tag}
  via = "semantic"     button / a / input / select / textarea / summary / [role=button] / [data-term]
        "pointer-only" cursor:pointer with no role — findable by eye, invisible to keyboard and screen-reader users
  salience = area × 1.5 if animated else area   (big loud things first; the impairment model's ordering)
Shared by explore_step.py (session-as-decider) and explore_run.py (scripted decider, sweeps).
"""
AFF_JS = r"""()=>{
  const SEM='button,a,[role=button],input,select,textarea,summary,[data-term]';
  const sem=new Set(document.querySelectorAll(SEM));
  const ptr=[...document.querySelectorAll('body *')].filter(e=>!sem.has(e)&&getComputedStyle(e).cursor==='pointer'&&!e.closest('button,a,[role=button],summary')
               &&!(e.parentElement&&getComputedStyle(e.parentElement).cursor==='pointer'));
  const cand=[...sem,...ptr];
  const vp={w:innerWidth,h:innerHeight};
  return cand.map(e=>{const r=e.getBoundingClientRect();
    const cs=getComputedStyle(e);
    const vis=r.width>0&&r.height>0&&r.bottom>0&&r.top<vp.h&&cs.visibility!=='hidden';
    if(!vis) return null;
    const area=r.width*r.height;
    const motion=(cs.animationName!=='none'||cs.transitionDuration!=='0s')?1.5:1;
    return {text:(e.getAttribute('aria-label')||e.textContent||e.value||e.placeholder||'').trim().replace(/\s+/g,' ').slice(0,48),
            via:sem.has(e)?'semantic':'pointer-only', tag:e.tagName.toLowerCase(),
            x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2),
            w:Math.round(r.width), h:Math.round(r.height),
            salience:Math.round(area*motion)};
  }).filter(Boolean);
}"""
