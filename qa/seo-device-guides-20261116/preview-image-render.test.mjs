/* TN-S5-MOBILE-IMAGE-RENDER-FIX-20261117 — pure regression suite for evaluateImageRender.
 * Per MANAGER_REVIEW 6955115055 update 2026-11-17T18:11:16Z FINAL CORRECTION 2:
 * required observations must FAIL CLOSED. Run: node qa/seo-device-guides-20261116/preview-image-render.test.mjs
 * Pure only: no browser/network/fs effects; fixtures mirror the real recorded observations. */
import { evaluateImageRender } from './preview-inject-candidate.js';
import assert from 'node:assert';

let pass = 0, fail = 0;
function ok(name, fn) {
  try { fn(); pass++; console.log('PASS ' + name); }
  catch (e) { fail++; console.log('FAIL ' + name + ': ' + e.message); }
}

const BASE = {
  found: true, tag: 'IMG',
  rect: { w: 295, h: 172, top: 281, bottom: 453, left: 40, right: 335 },
  viewport: { w: 390, h: 844 },
  offsetW: 295, offsetH: 172, display: 'block', visibility: 'visible',
  complete: true, naturalWidth: 960, loading_attr: 'lazy', currentSrc: '(resolved)',
  resource_entry: { transferSize: 0, decodedBodySize: 6615 },
  doc_overflow_px: 0,
};
const clone = (o) => JSON.parse(JSON.stringify(o));

ok('positive_green_sample_passes', () => {
  const v = evaluateImageRender(clone(BASE));
  assert.strictEqual(v.ok, true, 'failures=' + JSON.stringify(v.failures));
});
ok('recorded_zero_area_mobile_sample_fails', () => {
  const o = clone(BASE);
  o.rect = { w: 0, h: 0, top: 281, bottom: 281, left: 240, right: 240 };
  o.offsetW = 0; o.offsetH = 0;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('zero_rendered_width') && v.failures.includes('zero_rendered_height'), JSON.stringify(v.failures));
});
ok('offscreen_positive_size_fails', () => {
  const o = clone(BASE);
  o.rect = { w: 480, h: 280, top: 1000, bottom: 1280, left: 0, right: 480 };
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('no_two_dim_viewport_intersection'), JSON.stringify(v.failures));
});
ok('positive_document_overflow_fails', () => {
  const o = clone(BASE);
  o.doc_overflow_px = 202;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.some(f => String(f).indexOf('document_overflow_px_') === 0), JSON.stringify(v.failures));
});
ok('missing_doc_overflow_fails_closed', () => {
  const o = clone(BASE);
  delete o.doc_overflow_px;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('missing_or_nonfinite_doc_overflow'), JSON.stringify(v.failures));
});
ok('nan_doc_overflow_fails_closed', () => {
  const o = clone(BASE);
  o.doc_overflow_px = NaN;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('missing_or_nonfinite_doc_overflow'), JSON.stringify(v.failures));
  assert.ok(!JSON.stringify(v.failures).includes('document_overflow_px_'), 'NaN must not be stringified as a number failure');
});
ok('missing_display_observation_fails_closed', () => {
  const o = clone(BASE);
  delete o.display;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('missing_display_observation'), JSON.stringify(v.failures));
});
ok('missing_visibility_observation_fails_closed', () => {
  const o = clone(BASE);
  delete o.visibility;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('missing_visibility_observation'), JSON.stringify(v.failures));
});
ok('hidden_display_fails', () => {
  const o = clone(BASE);
  o.display = 'none';
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('hidden_or_clipped'), JSON.stringify(v.failures));
});
ok('nonfinite_rect_geometry_fails_closed', () => {
  const o = clone(BASE);
  o.rect.w = NaN;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('invalid_or_missing_rect_geometry'), JSON.stringify(v.failures));
  assert.ok(!v.failures.includes('zero_rendered_width'), 'geometry checks must be skipped on non-finite rect');
});
ok('invalid_viewport_fails_closed', () => {
  const o = clone(BASE);
  o.viewport = {};
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('invalid_or_missing_viewport'), JSON.stringify(v.failures));
});
ok('negative_doc_overflow_fails_closed_strict_zero', () => {
  const o = clone(BASE);
  o.doc_overflow_px = -5;
  const v = evaluateImageRender(o);
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.some(f => String(f).indexOf('document_overflow_px_') === 0), JSON.stringify(v.failures));
});
ok('image_not_found_fails', () => {
  const v = evaluateImageRender({ found: false });
  assert.strictEqual(v.ok, false);
  assert.ok(v.failures.includes('image_not_found'), JSON.stringify(v.failures));
});

console.log('TOTAL=' + (pass + fail) + ' PASS=' + pass + ' FAIL=' + fail);
if (fail > 0) process.exit(1);
