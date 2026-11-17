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
