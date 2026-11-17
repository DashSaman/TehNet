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
ok('marker: VM valid', () => { assert(S.isRunMarker(VM), 'VM=' + VM); });
ok('marker: rng=0 valid', () => { assert(S.isRunMarker(S.newRunMarker(1700000000000, 0))); });
ok('marker: rng=1 valid', () => { assert(S.isRunMarker(S.newRunMarker(1700000000000, 1))); });
throws('marker: junk reject', () => S.assertRunMarker('junk'), 'invalid run marker');
throws('daemon: no endpoint reject', () => S.evaluateDaemonTarget({ name: 'desktop-linux' }), 'no effective endpoint');
throws('daemon: ssh remote reject', () => S.evaluateDaemonTarget({ name: 'f', operating_system: 'linux', Endpoints: { docker: { Host: 'ssh://fixture.invalid' } } }), 'not a permitted owner-local target');
ok('daemon: npipe accept', () => { assert(S.evaluateDaemonTarget({ name: 'dl', operating_system: 'linux', Endpoints: { docker: { Host: 'npipe:////./pipe/dockerDesktopLinuxEngine' } } }).ok); });
ok('daemon: unix accept', () => { assert(S.evaluateDaemonTarget({ name: 'd', operating_system: 'linux', Host: 'unix:///var/run/docker.sock' }).ok); });
throws('img: empty req reject', () => S.evaluateImageAvailability([], {}), 'must be non-empty');
ok('img: null obs not ok', () => { assert(!S.evaluateImageAvailability(['wp:6'], null).ok); });
ok('img: observed IDs accept', () => { const v = S.evaluateImageAvailability(['wp:6', 'my:8'], { 'wp:6': { exit: 0, inspected: true, id: 'sha256:abc123def4567890abc123def4567890abc123def4567890abc123def4567890' }, 'my:8': { exit: 0, inspected: true, id: 'sha256:def456abc1237890def456abc1237890def456abc1237890def456abc1237890' } }); assert(v.ok); });
ok('img: garbage id not ok', () => { assert(!S.evaluateImageAvailability(['wp:6'], { 'wp:6': { exit: 0, inspected: true, id: 'xxxxxxxxxxxx' } }).ok); });
throws('img: no observed ID reject', () => S.assertImages(['not-installed:never'], {}), 'IMAGE BLOCKED');
throws('names: null existing reject', () => S.evaluateContainerNameUniqueness(null, ['a']), 'must be an array');
throws('names: null requested reject', () => S.evaluateContainerNameUniqueness([], null), 'must be an array');
throws('names: duplicate reject', () => S.evaluateContainerNameUniqueness([], ['dup', 'dup']), 'duplicates');
throws('names: null in requested reject', () => S.evaluateContainerNameUniqueness([], [null]), 'contains null');
ok('names: valid accept', () => { assert(S.evaluateContainerNameUniqueness(['other'], ['n1', 'n2']).ok); });
const PLAN = S.makePlan(VM, ["tn-syn-web-" + VM, "tn-syn-db-" + VM]);
S.verifyIdentity(PLAN, 'tn-syn-web-' + VM, 'docker-inspect');
S.verifyIdentity(PLAN, 'tn-syn-db-' + VM, 'docker-inspect');
ok('reg: registered null', () => { assert(S.ownershipRejectionReason(PLAN, 'tn-syn-web-' + VM) === null); });
ok('reg: prefix-extra not_in_reg', () => { assert(S.ownershipRejectionReason(PLAN, 'tn-syn-web-' + VM + '-extra') === 'not_in_plan'); });
ok('reg: foreign not_in_reg', () => { assert(S.ownershipRejectionReason(PLAN, 'other-container') === 'not_in_plan'); });
ok('clean: foreign-in-expected notOwned', () => { const v = S.evaluateCleanup(['foreign-test'], ['foreign-test'], PLAN); assert(!v.ok && v.notOwned.length > 0); });
ok('clean: full verified', () => {
  S.assertCleanupVerified(['tn-syn-web-' + VM, 'tn-syn-db-' + VM], ['tn-syn-web-' + VM, 'tn-syn-db-' + VM], PLAN, { success: true, remaining: [] });
});
throws('clean: no post-read unverified', () => {
  S.assertCleanupVerified(['tn-syn-web-' + VM, 'tn-syn-db-' + VM], ['tn-syn-web-' + VM, 'tn-syn-db-' + VM], PLAN, undefined);
}, 'malformed');
ok('clean: foreign deleted → ok=false with foreign listed', () => {
  const v = S.evaluateCleanup(['foreign-test'], ['tn-syn-web-' + VM], PLAN);
  assert(!v.ok && v.foreign.length > 0 && v.foreign[0] === 'foreign-test');
});
ok('read: exact both accept', () => { assert(S.evaluateMarkerReadability(VM, VM, VM).ok); });
throws('read: empty marker reject', () => S.evaluateMarkerReadability('', '', ''), 'invalid run marker');
ok('read: empty field reject', () => { assert(!S.evaluateMarkerReadability('', '', VM).ok); });
ok('read: prefix collision reject', () => { assert(!S.evaluateMarkerReadability(VM + '-extra', VM + '-extra', VM).ok); });
ok('read: suffix collision reject', () => { assert(!S.evaluateMarkerReadability('pre-' + VM, 'pre-' + VM, VM).ok); });
ok('read: wrong marker reject', () => { const v = S.evaluateMarkerReadability('TN-SYN-diff-123456', 'TN-SYN-diff-123456', VM); assert(!v.ok); });
console.log('TOTAL=' + (pass + fail) + ' PASS=' + pass + ' FAIL=' + fail);
if (fail > 0) process.exit(1);
