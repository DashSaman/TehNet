'use strict';
const assert = require('node:assert');
const S = require('./tn-synthetic-bootstrap.cjs');
let pass = 0, fail = 0;
function ok(name, fn) {
  try { fn(); pass++; console.log('PASS ' + name); }
  catch (e) { fail++; console.log('FAIL ' + name + ': ' + e.message); }
}
function throws(name, fn, expected) {
  try { fn(); fail++; console.log('FAIL ' + name + ': no throw'); }
  catch (e) {
    if (!expected || String(e.message).indexOf(expected) !== -1) { pass++; console.log('PASS ' + name); }
    else { fail++; console.log('FAIL ' + name + ': wrong error: ' + e.message); }
  }
}
const VM = S.newRunMarker(1700000000000, 0.5);
const SHA1 = 'sha256:abc123def4567890abc123def4567890abc123def4567890abc123def4567890';
const SHA2 = 'sha256:def456abc1237890def456abc1237890def456abc1237890def456abc1237890';
ok('marker: VM valid', () => { assert(S.isRunMarker(VM)); });
ok('marker: rng=0 valid', () => { assert(S.isRunMarker(S.newRunMarker(1700000000000, 0))); });
ok('marker: rng=1 valid', () => { assert(S.isRunMarker(S.newRunMarker(1700000000000, 1))); });
throws('marker: junk reject', () => S.assertRunMarker('junk'), 'invalid run marker');
throws('daemon: no endpoint reject', () => S.evaluateDaemonTarget({ name: 'desktop-linux' }), 'no effective endpoint');
throws('daemon: ssh remote reject', () => S.evaluateDaemonTarget({ name: 'f', operating_system: 'linux', Endpoints: { docker: { Host: 'ssh://fixture.invalid' } } }), 'not a permitted owner-local target');
throws('daemon: tcp remote reject', () => S.evaluateDaemonTarget({ name: 'f', operating_system: 'linux', Host: 'tcp://remote.host.invalid:2375' }), 'not a permitted owner-local target');
throws('daemon: https reject', () => S.evaluateDaemonTarget({ name: 'f', operating_system: 'linux', Host: 'https://fixture.invalid/localhost' }), 'not a permitted owner-local target');
ok('daemon: npipe accept', () => { assert(S.evaluateDaemonTarget({ name: 'dl', operating_system: 'linux', Endpoints: { docker: { Host: 'npipe:////./pipe/dockerDesktopLinuxEngine' } } }).ok); });
ok('daemon: unix accept', () => { assert(S.evaluateDaemonTarget({ name: 'd', operating_system: 'linux', Host: 'unix:///var/run/docker.sock' }).ok); });
ok('daemon: tcp localhost accept', () => { assert(S.evaluateDaemonTarget({ name: 't', operating_system: 'linux', Host: 'tcp://localhost:2375' }).ok); });
throws('daemon: conflicting reject', () => S.evaluateDaemonTarget({ name: 'f', operating_system: 'linux', Endpoints: { docker: { Host: 'npipe:////./pipe/dockerEngine' } }, Host: 'ssh://fixture.invalid' }), 'conflicting endpoint sources');
throws('img: empty req reject', () => S.evaluateImageAvailability([], {}), 'must be non-empty');
ok('img: null obs not ok', () => { assert(!S.evaluateImageAvailability(['wp:6'], null).ok); });
ok('img: name-only accept', () => {
  const v = S.evaluateImageAvailability(['wp:6'], { 'wp:6': { exit: 0, inspected: true, id: 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' } });
  assert(v.ok);
});
ok('img: pinned expected_id + matching obs accept', () => {
  const v = S.evaluateImageAvailability(
    [{ name: 'wp:6', expected_id: SHA1 }],
    { 'wp:6': { exit: 0, inspected: true, id: SHA1 } });
  assert(v.ok);
});
ok('img: valid-digest-wrong-ID → mismatch', () => {
  const v = S.evaluateImageAvailability(
    [{ name: 'wp:6', expected_id: SHA1 }],
    { 'wp:6': { exit: 0, inspected: true, id: SHA2 } });
  assert(!v.ok && v.mismatches.length === 1 && v.mismatches[0].image === 'wp:6');
});
ok('img: failed inspection not ok', () => {
  const v = S.evaluateImageAvailability(['wp:6'], { 'wp:6': { exit: 1, inspected: false, id: '' } });
  assert(!v.ok);
});
throws('img: garbage ID reject', () => S.assertImages(['wp:6'], { 'wp:6': { exit: 0, inspected: true, id: 'xxxxxxxxxxxx' } }), 'IMAGE BLOCKED');
throws('names: null existing reject', () => S.evaluateContainerNameUniqueness(null, ['a']), 'must be an array');
throws('names: duplicate reject', () => S.evaluateContainerNameUniqueness([], ['dup', 'dup']), 'duplicates');
throws('names: null in requested reject', () => S.evaluateContainerNameUniqueness([], [null]), 'contains null');
ok('names: valid accept', () => { assert(S.evaluateContainerNameUniqueness(['other'], ['n1', 'n2']).ok); });
const PLAN = S.makePlan(VM, ['tn-syn-web-' + VM, 'tn-syn-db-' + VM]);
ok('plan: identity_not_verified before verifyIdentity', () => {
  assert(S.ownershipRejectionReason(PLAN, 'tn-syn-web-' + VM) === 'identity_not_verified');
});
ok('cleanup: unverified plan returns notOwned', () => {
  const v = S.evaluateCleanup(['tn-syn-web-' + VM], ['tn-syn-web-' + VM], PLAN);
  assert(!v.ok && v.notOwned.length > 0);
});
ok('verifyIdentity: structured binding accepted', () => {
  S.verifyIdentity(PLAN, 'tn-syn-web-' + VM, { container_id: 'sha256:abc123def4567890', run_marker: VM });
});
ok('cleanup: after verifyIdentity → ok', () => {
  const v = S.evaluateCleanup(['tn-syn-web-' + VM], ['tn-syn-web-' + VM], PLAN);
  assert(v.ok);
});
throws('verifyIdentity: unrelated evidence rejected', () => {
  S.verifyIdentity(PLAN, 'tn-syn-db-' + VM, 'unrelated');
}, 'identity_binding: missing or not object');
throws('cleanup: constructor key reject', () => {
  S.evaluateCleanup(['constructor'], ['constructor'], PLAN);
}, 'inherited prototype key');
throws('post-read: non-string entry reject', () => {
  S.evaluatePostRead({ success: true, remaining: [{ name: 'web' }] }, PLAN);
}, 'non-string remaining entry');
throws('post-read: string top-level reject', () => {
  S.evaluatePostRead('not-an-object', PLAN);
}, 'malformed');
throws('post-read: failed read reject', () => {
  S.evaluatePostRead({ success: false, remaining: [] }, PLAN);
}, 'read failure');
throws('post-read: null reject', () => {
  S.evaluatePostRead(null, PLAN);
}, 'malformed');
ok('post-read: valid empty inventory accept', () => {
  const v = S.evaluatePostRead({ success: true, remaining: [] }, PLAN);
  assert(v.verified === true);
});
throws('cleanup: no post-read → unverified', () => {
  S.assertCleanupVerified(['tn-syn-web-' + VM], ['tn-syn-web-' + VM], PLAN, undefined);
}, 'CLEANUP UNVERIFIED');
ok('read: exact both accept', () => { assert(S.evaluateMarkerReadability(VM, VM, VM).ok); });
throws('read: empty marker reject', () => S.evaluateMarkerReadability('', '', ''), 'invalid run marker');
ok('read: empty field reject', () => { assert(!S.evaluateMarkerReadability('', '', VM).ok); });
ok('read: prefix collision reject', () => { assert(!S.evaluateMarkerReadability(VM + '-extra', VM + '-extra', VM).ok); });
ok('read: suffix collision reject', () => { assert(!S.evaluateMarkerReadability('pre-' + VM, 'pre-' + VM, VM).ok); });
ok('read: wrong marker reject', () => { const v = S.evaluateMarkerReadability('TN-SYN-diff-123456', 'TN-SYN-diff-123456', VM); assert(!v.ok); });
console.log('TOTAL=' + (pass + fail) + ' PASS=' + pass + ' FAIL=' + fail);
if (fail > 0) process.exit(1);
