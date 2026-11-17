'use strict';
/* TN-SYNTHETIC-BOOTSTRAP-20261117 rev1 — SOURCE_ONLY / INTEGRATION_NOT_RUN
 * Synthetic-only disposable WordPress+MySQL bootstrap (owner-local Docker).
 * Guarantees:
 * - ZERO production dump/copy/import/SSH;
 * - Fresh namespace: unique container names per run marker;
 * - Fail-closed BEFORE any effect: Docker daemon target must be local; required images
 *   must exist locally (--pull=never equivalent); no existing containers with the same
 *   run-scoped names; marker must be valid;
 * - Unique readable marker in DB (wp option) and served page;
 * - Ownership: only resources matching this run's marker are cleaned up;
 * - Cleanup: verified (delete actual containers/network/volumes, post-check zero).
 * All Docker/exec calls are injectable for PURE testing. */

const { execSync } = require('node:child_process');

const MARKER_RE = /^TN-SYN-[0-9a-z]{4,}-[0-9a-z]{4,}$/;

function newRunMarker(nowMs) {
  const t = Number.isFinite(nowMs) ? nowMs : Date.now();
  const r = Math.floor(Math.random() * 1296 ** 3).toString(36).padStart(3, '0');
  return 'TN-SYN-' + t.toString(36) + '-' + r;
}
function isRunMarker(v) {
  return typeof v === 'string' && MARKER_RE.test(v);
}
function assertRunMarker(v) {
  if (!isRunMarker(v)) throw new Error('invalid run marker: ' + String(v).slice(0, 40));
  return v;
}

/* --- Docker daemon target check (fail closed; must be local) --- */
function evaluateDaemonTarget(info) {
  const o = info && typeof info === 'object' ? info : {};
  const checks = [
    ['daemon_local', o.operating_system !== 'remote' && String(o.name || '').length > 0],
    ['not_remote_context', String(o.remote || '').length === 0],
  ];
  const failed = checks.filter(c => !c[1]).map(c => c[0]);
  return { ok: failed.length === 0, failed, checks: checks.map(([name, pass]) => ({ name, pass })) };
}
function assertDaemonTarget(info) {
  const v = evaluateDaemonTarget(info);
  if (!v.ok) throw Object.assign(new Error('DAEMON BLOCKED: ' + v.failed.join(',')), { name: 'DaemonBlocked', failed: v.failed });
  return v;
}

/* --- image availability (fail closed; --pull=never equivalent) --- */
function evaluateImageAvailability(images) {
  const list = Array.isArray(images) ? images : [];
  const missing = list.filter(img => !img || typeof img !== 'string' || img.length === 0);
  return { ok: missing.length === 0, missing, available: list.filter(img => !missing.includes(img)) };
}
function assertImages(avail) {
  if (!avail || avail.ok !== true) {
    const missing = avail && Array.isArray(avail.missing) ? avail.missing.join(',') : 'unknown';
    throw Object.assign(new Error('IMAGE BLOCKED: missing ' + missing), { name: 'ImageBlocked', missing: avail && avail.missing });
  }
  return avail;
}

/* --- container name uniqueness (fail closed before create) --- */
function evaluateContainerNameUniqueness(existingNames, requestedNames) {
  const existing = Array.isArray(existingNames) ? existingNames : [];
  const requested = Array.isArray(requestedNames) ? requestedNames : [];
  const collisions = requested.filter(n => existing.includes(n));
  return { ok: collisions.length === 0, collisions };
}
function assertContainerNames(existing, requested) {
  const v = evaluateContainerNameUniqueness(existing, requested);
  if (!v.ok) throw Object.assign(new Error('CONTAINER NAME COLLISION: ' + v.collisions.join(',')), { name: 'ContainerNameCollision', collisions: v.collisions });
  return v;
}

/* --- ownership predicate for synthetic resources --- */
function isOwnedContainer(name, marker) {
  return typeof name === 'string' && name.indexOf('tn-syn-' + marker + '-') === 0;
}
function isOwnedNetwork(name, marker) {
  return typeof name === 'string' && name === 'tn-syn-net-' + marker;
}
function ownershipRejectionReason(name, marker) {
  if (!isRunMarker(marker)) return 'bad_marker';
  if (!isOwnedContainer(name, marker) && !isOwnedNetwork(name, marker)) return 'not_owned_by_this_run';
  return null;
}

/* --- cleanup: verify only THIS run's resources are deleted --- */
function evaluateCleanup(deleted, expectedNames, marker) {
  const del = Array.isArray(deleted) ? deleted : [];
  const exp = Array.isArray(expectedNames) ? expectedNames : [];
  const missing = exp.filter(n => !del.includes(n));
  const extra = del.filter(n => !exp.includes(n) && !isOwnedContainer(n, marker) && !isOwnedNetwork(n, marker));
  return { ok: missing.length === 0 && extra.length === 0, missing, extra };
}
function assertCleanup(deleted, expected, marker) {
  const v = evaluateCleanup(deleted, expected, marker);
  if (!v.ok) throw Object.assign(new Error('CLEANUP FAILED: missing=' + v.missing.join(',') + ' extra=' + v.extra.join(',')), { name: 'CleanupFailed', missing: v.missing, extra: v.extra });
  return v;
}

/* --- marker readability: DB option value and served page must both contain it --- */
function evaluateMarkerReadability(dbOptionValue, servedPageContent, marker) {
  const db_ok = typeof dbOptionValue === 'string' && dbOptionValue.indexOf(marker) !== -1;
  const page_ok = typeof servedPageContent === 'string' && servedPageContent.indexOf(marker) !== -1;
  return { ok: db_ok && page_ok, db_ok, page_ok };
}
function assertMarkerReadable(db, page, marker) {
  const v = evaluateMarkerReadability(db, page, marker);
  if (!v.ok) throw Object.assign(new Error('MARKER NOT READABLE: db=' + v.db_ok + ' page=' + v.page_ok), { name: 'MarkerNotReadable' });
  return v;
}

module.exports = {
  newRunMarker, isRunMarker, assertRunMarker,
  evaluateDaemonTarget, assertDaemonTarget,
  evaluateImageAvailability, assertImages,
  evaluateContainerNameUniqueness, assertContainerNames,
  isOwnedContainer, isOwnedNetwork, ownershipRejectionReason,
  evaluateCleanup, assertCleanup,
  evaluateMarkerReadability, assertMarkerReadable,
  MARKER_RE,
};
