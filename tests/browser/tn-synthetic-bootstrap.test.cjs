'use strict';
/* PURE tests for tn-synthetic-bootstrap.cjs — all Docker/exec stubbed, zero effects. */
const assert = require('node:assert');
const S = require('./tn-synthetic-bootstrap.cjs');
let pass = 0, fail = 0;
function ok(name, fn) {
  try { fn(); pass++; console.log('PASS ' + name); }
  catch (e) { fail++; console.log('FAIL ' + name + ' → ' + e.message); }
}
function throws(name, fn, expected) {
  try { fn(); fail++; console.log('FAIL ' + name + ' → no throw'); }
  catch (e) {
    if (!expected || e.message.indexOf(expected) !== -1) { pass++; console.log('PASS ' + name); }
    else { fail++; console.log('FAIL ' + name + ' → wrong error: ' + e.message); }
  }
}

/* marker */
ok('marker: valid shape accepted', () => { assert(S.isRunMarker(S.newRunMarker())); });
ok('marker: deterministic with explicit time', () => {
  const m = S.newRunMarker(1700000000000);
  assert(m.indexOf('TN-SYN-') === 0);
});
throws('marker: junk rejected', () => S.assertRunMarker('junk'), 'invalid run marker');

/* daemon target */
ok('daemon: local accepted', () => {
  const v = S.evaluateDaemonTarget({ name: 'desktop-linux', operating_system: 'linux' });
  assert(v.ok === true);
});
throws('daemon: remote rejected', () => S.assertDaemonTarget({ name: 'remote-prod', remote: 'tcp://prod:2375' }), 'DAEMON BLOCKED');

/* image availability */
ok('images: all present accepted', () => {
  const v = S.evaluateImageAvailability(['wordpress:6.4', 'mysql:8.0']);
  assert(v.ok === true);
});
throws('images: missing rejected', () => S.assertImages({ ok: false, missing: ['wordpress:6.4'] }), 'IMAGE BLOCKED');

/* container name uniqueness */
ok('names: no collision accepted', () => {
  const v = S.evaluateContainerNameUniqueness(['other'], ['tn-syn-TN-SYN-x-abc-web']);
  assert(v.ok === true);
});
throws('names: collision rejected', () => S.assertContainerNames(['tn-syn-TN-SYN-x-abc-web'], ['tn-syn-TN-SYN-x-abc-web']), 'CONTAINER NAME COLLISION');

/* ownership */
ok('ownership: owned container accepted', () => {
  assert(S.isOwnedContainer('tn-syn-TN-SYN-x-abc-web', 'TN-SYN-x-abc'));
});
ok('ownership: foreign container rejected', () => {
  assert(!S.isOwnedContainer('tehnet-wordpress', 'TN-SYN-x-abc'));
});
ok('ownership: bad marker returns bad_marker reason', () => {
  const reason = S.ownershipRejectionReason('tn-syn-web', 'junk');
  assert(reason === 'bad_marker');
});

/* cleanup */
ok('cleanup: complete + no extras accepted', () => {
  const v = S.evaluateCleanup(['tn-syn-TN-SYN-x-abc-web', 'tn-syn-TN-SYN-x-abc-db', 'tn-syn-net-TN-SYN-x-abc'],
    ['tn-syn-TN-SYN-x-abc-web', 'tn-syn-TN-SYN-x-abc-db', 'tn-syn-net-TN-SYN-x-abc'], 'TN-SYN-x-abc');
  assert(v.ok === true);
});
ok('cleanup: incomplete deletion fails', () => {
  const v = S.evaluateCleanup(['tn-syn-TN-SYN-x-abc-web'], ['tn-syn-TN-SYN-x-abc-web', 'tn-syn-TN-SYN-x-abc-db', 'tn-syn-net-TN-SYN-x-abc'], 'TN-SYN-x-abc');
  assert(v.ok === false && v.missing.length === 2);
});
ok('cleanup: extra foreign resource deletion fails', () => {
  const v = S.evaluateCleanup(['tn-syn-TN-SYN-x-abc-web', 'tehnet-wordpress'], ['tn-syn-TN-SYN-x-abc-web'], 'TN-SYN-x-abc');
  assert(v.ok === false && v.extra.length > 0);
});

/* marker readability */
ok('marker readability: DB + page both contain it', () => {
  const v = S.evaluateMarkerReadability('Marker: TN-SYN-x-abc', '<body>TN-SYN-x-abc</body>', 'TN-SYN-x-abc');
  assert(v.ok === true);
});
throws('marker readability: missing in DB throws', () => S.assertMarkerReadable(null, '<body>TN-SYN-x-abc</body>', 'TN-SYN-x-abc'), 'MARKER NOT READABLE');

console.log('\nTOTAL=' + (pass + fail) + ' PASS=' + pass + ' FAIL=' + fail);
if (fail > 0) process.exit(1);
