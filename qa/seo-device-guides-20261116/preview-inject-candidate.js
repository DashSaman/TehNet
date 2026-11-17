// TN-CANDIDATE-PREVIEW-HARNESS v1 (2026-11-17) — replayable preview integration
// for the scoped candidate stylesheet (qa artifact, LOCAL preview only).
//
// Replay recipe (existing tools, no new software):
//   1. python -I preview-server.py 8138            (serves content tree, UTF-8)
//   2. import this module in the Node REPL browser runtime;
//      cssText = loadCss()
//   3. per page (m2/m3/s5) and per viewport (desktop 1280x900, mobile 390x844):
//        tab.goto(url); waitForLoadState('domcontentloaded')
//        evaluate(injectJs(cssText))               -> injects candidate-preview.css verbatim
//        evaluate(wrapJs)                          -> tabindex+aria-label on pre/table containers
//        evaluate(metricsJs)                       -> images, document overflow, contained overflow
//        keyboard probe via real Tab/ArrowRight keypresses (see probe note in receipt)
//   4. bind in the receipt: css sha256, this file's sha256, page MD/HTML sha256,
//      git HEAD, UTC and the six page/viewport results (m2/m3/s5 x desktop/mobile).
//
// Generated content files are NOT modified; WordPress/theme/KSES NOT_RUN.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));

export function loadCss() {
  return fs.readFileSync(path.join(DIR, 'candidate-preview.css'), 'utf8');
}

/** Inject the exact CSS text verbatim as one <style id="tn-candidate-preview"> */
export const injectJs = (cssText) =>
  "(() => { const s=document.createElement('style'); s.id='tn-candidate-preview';" +
  ' s.textContent=' + JSON.stringify(cssText) + ';' +
  " document.head.appendChild(s); return { injected: s.id }; })()";

/** Make horizontal-scroll containers keyboard-accessible (real Tab targets).
 * Idempotent: skips elements already tagged. Returns counts only. */
export const wrapJs =
  "(() => { const els=[...document.querySelectorAll('pre, table')];" +
  ' let tagged=0, already=0;' +
  ' els.forEach(el => {' +
  "   if (!el.hasAttribute('tabindex')) { el.setAttribute('tabindex','0'); tagged++; } else { already++; }" +
  "   if (!el.hasAttribute('aria-label')) {" +
  "     el.setAttribute('aria-label', el.tagName==='PRE'" +
  "       ? '\u0628\u0644\u0648\u06a9 \u06a9\u062f \u2014 \u0642\u0627\u0628\u0644 \u067e\u06cc\u0645\u0627\u06cc\u0634 \u0627\u0641\u0642\u06cc \u0628\u0627 \u06a9\u06cc\u0628\u0648\u0631\u062f'" +
  "       : '\u062c\u062f\u0648\u0644 \u2014 \u0642\u0627\u0628\u0644 \u067e\u06cc\u0645\u0627\u06cc\u0634 \u0627\u0641\u0642\u06cc \u0628\u0627 \u06a9\u06cc\u0628\u0648\u0631\u062f'); }" +
  ' });' +
  ' return { containers_total: els.length, containers_tagged_new: tagged, containers_already_tagged: already,' +
  "   pre: els.filter(e=>e.tagName==='PRE').length, table: els.filter(e=>e.tagName==='TABLE').length }; })()";

/** Metrics after inject+wrap: images, DOCUMENT overflow, and CONTAINED overflow
 * (inner scrollable content of each pre/table — contained means it scrolls inside
 * the container instead of widening the document; document overflow must be 0). */
export const metricsJs =
  "(() => ({ images_total: document.querySelectorAll('img').length," +
  ' images_loaded: [...document.querySelectorAll("img")].filter(i=>i.complete && i.naturalWidth>0).length,' +
  ' doc_overflow_px: document.documentElement.scrollWidth - document.documentElement.clientWidth,' +
  ' pre_total: document.querySelectorAll("pre").length,' +
  ' pre_with_inner_scroll: [...document.querySelectorAll("pre")].filter(p=>p.scrollWidth>p.clientWidth).length,' +
  ' table_total: document.querySelectorAll("table").length,' +
  ' table_with_inner_scroll: [...document.querySelectorAll("table")].filter(t=>t.scrollWidth>t.clientWidth).length,' +
  ' containers_focusable: document.querySelectorAll("pre[tabindex], table[tabindex]").length }))()';

/** activeElement read helper (used after each real Tab keypress) */
export const activeJs =
  "(() => { const el=document.activeElement; return { tag: el?el.tagName:null," +
  ' cls: el&&el.getAttribute?el.getAttribute("class"):null }; })()';

/** scrollLeft read for the focused container (before/after ArrowRight) */
export const scrollLeftJs =
  "(() => { const el=document.activeElement;" +
  ' return el && (el.tagName==="PRE"||el.tagName==="TABLE")' +
  ' ? { tag: el.tagName, scrollLeft: el.scrollLeft, scrollWidth: el.scrollWidth, clientWidth: el.clientWidth }' +
  ' : { tag: el?el.tagName:null, scrollLeft: null }; })()';

/* --- TN-S5-MOBILE-IMAGE-RENDER-FIX-20261117: reusable image-render visibility check ---
 * RED symptom this check exists for: at 390x844 the lazy SVG loaded (complete=true,
 * naturalWidth>0) yet rendered 0x0 (ancestor figure width 0) while an old record called
 * it "visible" from its vertical coordinate alone. Load facts are NOT display proof.
 * Additive exports only: existing inject/wrap/metrics behavior is unchanged. */

/** Page-side observation (read-only; evaluate via tab.playwright.evaluate).
 * Captures the tutorial's main figure image: rendered box, viewport box, ancestor
 * chain boxes/computed styles, matched committed CSS rules, load facts, doc overflow. */
export const imageRenderObsJs =
  "(() => { const i=document.querySelector('figure img'); if(!i) return { found:false }; " +
  ' const r=i.getBoundingClientRect(); const vw=window.innerWidth, vh=window.innerHeight; ' +
  ' const chain=[]; let el=i; for(let d=0; d<5 && el; d++){ const rc=el.getBoundingClientRect(); const cs=getComputedStyle(el); ' +
  " chain.push({ depth:d, tag:el.tagName, cls:el.getAttribute&&el.getAttribute('class')||null, rect_w:Math.round(rc.width), rect_h:Math.round(rc.height), " +
  " display:cs.display, width:cs.width, maxWidth:cs.maxWidth, minWidth:cs.minWidth, marginLeft:cs.marginLeft, marginRight:cs.marginRight, " +
  ' overflowX:cs.overflowX, position:cs.position }); el=el.parentElement; } ' +
  ' const matched=[]; try { for(const sheet of document.styleSheets){ let rules; try{ rules=sheet.cssRules; }catch(e){ continue; } ' +
  ' for(const rule of (rules||[])){ if(!rule.selectorText) continue; ' +
  " let m=false; try{ m=i.matches(rule.selectorText); }catch(e){} if(m) matched.push({ target:\'img\', css:rule.style.cssText.slice(0,200) }); " +
  " if(i.closest('figure')){ let mf=false; try{ mf=i.closest('figure').matches(rule.selectorText); }catch(e){} if(mf) matched.push({ target:\'figure\', css:rule.style.cssText.slice(0,200) }); } " +
  ' } } } catch(e) { matched.push({ error:String(e).slice(0,80) }); } ' +
  ' const e=performance.getEntriesByType("resource").find(x=>x.name.indexOf("tutorial-s5")>=0); ' +
  ' return { found:true, tag:i.tagName, rect:{ w:Math.round(r.width), h:Math.round(r.height), top:Math.round(r.top), bottom:Math.round(r.bottom), left:Math.round(r.left), right:Math.round(r.right) }, ' +
  ' viewport:{ w:vw, h:vh }, scrollY:Math.round(window.scrollY), ' +
  " offsetW:i.offsetWidth, offsetH:i.offsetHeight, display:getComputedStyle(i).display, visibility:getComputedStyle(i).visibility, " +
  " complete:i.complete, naturalWidth:i.naturalWidth, loading_attr:i.getAttribute('loading'), currentSrc:i.currentSrc?'(resolved)':'(empty)', " +
  ' resource_entry:e?{ transferSize:e.transferSize, decodedBodySize:e.decodedBodySize }:null, ' +
  " doc_overflow_px:document.documentElement.scrollWidth-document.documentElement.clientWidth, ancestor_chain:chain, matched_rules:matched }; })()";

/** Pure predicate over imageRenderObsJs output. Pass requires ACTUAL DISPLAY:
 * finite required geometry/viewport observations, positive rendered width AND
 * height, positive two-dimensional viewport intersection, loaded asset, present
 * computed display/visibility observations that are not hidden, and a FINITE
 * observed document overflow exactly equal to zero.
 * Load facts (complete/naturalWidth) alone never satisfy this check, and a
 * partial/unusable observation (missing or NaN required fields) FAILS CLOSED. */
export function evaluateImageRender(obs) {
  if (!obs || obs.found === false) return { ok: false, failures: ['image_not_found'] };
  const failures = [];
  const r = obs.rect || {};
  const v = obs.viewport || {};
  const finite = (x) => typeof x === 'number' && Number.isFinite(x);
  const geoOk = ['w', 'h', 'top', 'bottom', 'left', 'right'].every(k => finite(r[k]));
  const vpOk = finite(v.w) && finite(v.h) && v.w > 0 && v.h > 0;
  if (!geoOk) failures.push('invalid_or_missing_rect_geometry');
  if (!vpOk) failures.push('invalid_or_missing_viewport');
  if (!(obs.complete === true)) failures.push('asset_not_complete');
  if (!(finite(obs.naturalWidth) && obs.naturalWidth > 0)) failures.push('naturalWidth_not_positive');
  if (geoOk) {
    if (!(r.w > 0)) failures.push('zero_rendered_width');
    if (!(r.h > 0)) failures.push('zero_rendered_height');
  }
  if (geoOk && vpOk) {
    const horiz = Math.min(r.right, v.w) - Math.max(r.left, 0);
    const vert = Math.min(r.bottom, v.h) - Math.max(r.top, 0);
    if (!(Number.isFinite(horiz) && Number.isFinite(vert) && horiz > 0 && vert > 0))
      failures.push('no_two_dim_viewport_intersection');
  }
  /* required computed-style observations must be PRESENT before hidden checks */
  if (typeof obs.display !== 'string' || obs.display.length === 0) failures.push('missing_display_observation');
  if (typeof obs.visibility !== 'string' || obs.visibility.length === 0) failures.push('missing_visibility_observation');
  if (obs.display === 'none' || obs.visibility === 'hidden' || obs.visibility === 'collapse') failures.push('hidden_or_clipped');
  /* required document-overflow observation: must be finite and exactly zero */
  if (!finite(obs.doc_overflow_px)) failures.push('missing_or_nonfinite_doc_overflow');
  else if (obs.doc_overflow_px !== 0) failures.push('document_overflow_px_' + obs.doc_overflow_px);
  return { ok: failures.length === 0, failures, rendered: { w: r.w, h: r.h }, viewport: v, loaded: { complete: obs.complete, naturalWidth: obs.naturalWidth } };
}

/* --- TN-S4C-ENDPOINT-TABLE-MOBILE-READABILITY-20261118: S4-scoped presentation hook ---
 * Additive exports only; existing exports/behavior untouched. Guarded to fire ONLY on
 * the S4 lesson's single 9-column endpoint table (identified by its unique synthetic
 * address 192.168.10.99/24 AND a 9-cell header); on every other page the functions
 * return {applied:false} without touching the DOM. */

/** Loads the S4-scoped presentation stylesheet (separate artifact; shared candidate CSS untouched). */
export function loadS4EndpointPresentationCss() {
  return fs.readFileSync(path.join(DIR, 's4-endpoint-presentation.css'), 'utf8');
}

/** Builds the S4-scoped presentation injection script. cssText = content of
 * s4-endpoint-presentation.css (single source of truth), embedded via JSON.stringify.
 * The script injects the <style> and tags the endpoint table + its wrapping figure
 * (tabindex/aria) so the ACTUAL horizontal overflow container (the figure wrapper) is
 * keyboard-accessible. Guarded: applies only when the unique endpoint marker is present. */
export function s4EndpointPresentationJs(cssText) {
  return "(() => { const cssText=" + JSON.stringify(cssText) + "; " +
  " const tables=[...document.querySelectorAll('table')]; " +
  " const t=tables.find(function(x){ return x.textContent.indexOf('192.168.10.99/24') >= 0 && x.querySelectorAll('thead th').length === 9; }); " +
  " if(!t) return { applied:false, reason:'S4 endpoint table not found on this page' }; " +
  " if(document.getElementById('tn-s4-endpoint-presentation')) return { applied:false, reason:'presentation style already present' }; " +
  ' const st=document.createElement(\'style\'); st.id=\'tn-s4-endpoint-presentation\'; ' +
  ' st.textContent=cssText; ' +
  ' document.head.appendChild(st); ' +
  " t.classList.add('tn-s4-endpoint'); " +
  " const fig=t.closest('figure'); let figTagged=false; " +
  ' if(fig){ fig.classList.add(\'tn-s4-endpoint-wrap\'); if(!fig.hasAttribute(\'tabindex\')){ fig.setAttribute(\'tabindex\',\'0\'); figTagged=true; } ' +
  " if(!fig.hasAttribute('aria-label')) fig.setAttribute('aria-label','جدول endpoint S4 — قابل پیمایش افقی با کلید'); } " +
  ' const r=t.getBoundingClientRect(); ' +
  ' return { applied:true, table_class_added:true, figure_wrapped:!!fig, figure_tabindex_set:figTagged, table_w:Math.round(r.width), header_cells:t.querySelectorAll(\'thead th\').length, body_rows:t.querySelectorAll(\'tbody tr\').length, style_id:\'tn-s4-endpoint-presentation\' }; })()';
}
