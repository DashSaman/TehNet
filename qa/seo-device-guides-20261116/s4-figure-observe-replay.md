# TN-S4C-ENDPOINT-TABLE-MOBILE-READABILITY-20261118 — exact S4 figure-observation replay recipe

Concise replay using ONLY the existing committed exports of
`qa/seo-device-guides-20261116/preview-inject-candidate.js`
(loadCss, injectJs, wrapJs, loadS4EndpointPresentationCss, s4EndpointPresentationJs).
The generic `scrollLeftJs` export only accepts PRE/TABLE and is NOT used here; the
FIGURE observation is the dedicated read-only snippet below. No scroll-property
assignment, no synthetic keys in this observation.

## Steps (per viewport)

1. Fresh load of `http://127.0.0.1:8138/tutorials/s4-vlan-switch-l2.gutenberg.html`
   (wait for `domcontentloaded`; set viewport: 1280×900 or 390×844).
2. Base injection/wrap (existing exports):
   - `evaluate(injectJs(loadCss()))`
   - `evaluate(wrapJs)`
3. S4-scoped presentation (guarded hook; fires only on the unique endpoint marker):
   - `evaluate(s4EndpointPresentationJs(loadS4EndpointPresentationCss()))`
4. Scroll the wrapper into view (scrollIntoView is positioning only; it is not the proof).
5. Focus the ACTUAL overflow container and drive it with REAL keys via the browser
   input path (`cua.keypress` ArrowRight/ArrowLeft), reading absolute `scrollLeft`
   before/after each key from `document.activeElement` (must be the FIGURE).

## Dedicated read-only FIGURE observation snippet (evaluate string)

```js
(() => {
  const f = document.querySelector('figure.tn-s4-endpoint-wrap');
  if (!f) return { found: false };
  const r = f.getBoundingClientRect();
  const cs = getComputedStyle(f);
  return {
    found: true, tag: 'FIGURE',
    tabindex: f.getAttribute('tabindex'),
    aria_label: f.getAttribute('aria-label'),
    active_is_figure: document.activeElement === f,
    scrollWidth: f.scrollWidth, clientWidth: f.clientWidth,
    scrollLeft_abs: f.scrollLeft,
    overflow_x: cs.overflowX,
    table_class: (t => t ? t.className : null)(f.querySelector('table')),
    table_display: getComputedStyle(f.querySelector('table')).display,
    header_cells: f.querySelectorAll('thead th').length,
    body_rows: f.querySelectorAll('tbody tr').length,
    doc_overflow_px: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()
```

## Binding

Every run binds: pre-work `git rev-parse HEAD`, served-byte SHA256 equality with the
built file, candidate-preview.css sha256, preview-inject-candidate.js sha256,
s4-endpoint-presentation.css sha256, S4 MD/HTML sha256, viewport, and per-pass
start/end UTC from the host clock. Observations are read-only: no scroll-property
assignment, no synthetic keys, no forcing of image state.
