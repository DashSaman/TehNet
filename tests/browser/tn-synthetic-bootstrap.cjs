'use strict';
/* TN-SYNTHETIC-BOOTSTRAP-20261117 rev2 — PREDICATE_CONTRACT_DRAFT / BOOTSTRAP_LIFECYCLE_NOT_IMPLEMENTED
 * Corrections per MANAGER_REVIEW 6944753704 (all six counterexamples addressed).
 * SOURCE_ONLY / INTEGRATION_NOT_RUN — no bootstrap entry point, no lifecycle adapter,
 * no executor injection claim. Pure predicates with strict input validation.
 * All previous title-equality/base-attribution/P2-driver-row corrections preserved. */

const MARKER_RE = /^TN-SYN-[0-9a-z]{6,}-[0-9a-z]{6,}$/;

function newRunMarker(nowMs, rngValue) {
  const t = Number.isFinite(nowMs) ? Math.floor(nowMs) : Date.now();
  const rng = Number.isFinite(rngValue) ? Math.max(0, Math.min(1, rngValue)) : Math.random();
  const suffix = Math.floor(rng * 1296 ** 3).toString(36).padStart(6, '0').slice(0, 6);
  return 'TN-SYN-' + t.toString(36).padStart(6, '0') + '-' + suffix;
}
function isRunMarker(v) {
  return typeof v === 'string' && MARKER_RE.test(v);
}
function assertRunMarker(v) {
  if (!isRunMarker(v)) throw new Error('invalid run marker: ' + String(v).slice(0, 60));
  return v;
}
function requireString(v, label) {
  if (typeof v !== 'string' || v.trim().length === 0) throw new Error(label + ': missing or empty');
  return v.trim();
}
function requireArray(v, label) {
  if (!Array.isArray(v)) throw new Error(label + ': must be an array');
  if (v.length === 0) throw new Error(label + ': must be non-empty');
  return v;
}
function requireObject(v, label) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) throw new Error(label + ': missing or not object');
  return v;
}

function evaluateDaemonTarget(info) {
  requireObject(info, 'daemon_info');
  const ep = info.Endpoints && info.Endpoints.docker && typeof info.Endpoints.docker.Host === 'string' && info.Endpoints.docker.Host.length > 0
    ? info.Endpoints.docker.Host
    : typeof info.Host === 'string' && info.Host.length > 0 ? info.Host : null;
  if (!ep) throw new Error('DAEMON: no effective endpoint observed (name alone insufficient)');
  if (/^ssh:\/\//.test(ep)) throw new Error('DAEMON: remote ssh endpoint rejected');
  if (/^tcp:\/\//.test(ep) && ep.indexOf('localhost') < 0 && ep.indexOf('127.0.0.1') < 0)
    throw new Error('DAEMON: remote tcp endpoint rejected');
  const localPipe = ep.indexOf('npipe:////./pipe/docker') === 0 || ep.indexOf('unix:///var/run/docker.sock') === 0;
  if (!localPipe && !ep.startsWith('unix://') && !ep.startsWith('npipe:////./pipe/docker') && ep.indexOf('localhost') < 0 && ep.indexOf('127.0.0.1') < 0)
    throw new Error('DAEMON: unrecognized endpoint "' + ep + '"');
  return { ok: true, endpoint: ep };
}
function assertDaemonTarget(info) {
  const v = evaluateDaemonTarget(info);
  if (!v.ok) throw Object.assign(new Error('DAEMON BLOCKED'), { name: 'DaemonBlocked', failed: v });
  return v;
}

function evaluateImageAvailability(requiredImages, observedImages) {
  requireArray(requiredImages, 'required_images');
  for (const img of requiredImages) {
    if (typeof img !== 'string' || img.trim().length === 0) throw new Error('required_images: empty entry');
  }
  if (!observedImages || typeof observedImages !== 'object' || Array.isArray(observedImages))
    return { ok: false, missing: requiredImages.slice(), observed_ids: {} };
  const missing = [];
  const observed_ids = {};
  for (const img of requiredImages) {
    const obs = observedImages[img];
    if (!obs || typeof obs !== 'object' || typeof obs.id !== 'string' || obs.id.length < 12)
      missing.push(img);
    else observed_ids[img] = obs.id;
  }
  return { ok: missing.length === 0, missing, observed_ids };
}
function assertImages(required, observed) {
  const v = evaluateImageAvailability(required, observed);
  if (!v.ok) throw Object.assign(new Error('IMAGE BLOCKED: missing ' + v.missing.join(',')), { name: 'ImageBlocked', missing: v.missing });
  return v;
}

function evaluateContainerNameUniqueness(existingNames, requestedNames) {
  if (!Array.isArray(existingNames)) throw new Error('existing_names: must be an array');
  if (!Array.isArray(requestedNames)) throw new Error('requested_names: must be an array');
  if (requestedNames.length === 0) throw new Error('requested_names: empty');
  for (const n of requestedNames) {
    if (typeof n !== 'string' || n.length === 0) throw new Error('requested_names: contains null/empty/invalid name');
  }
  const dupes = requestedNames.filter((n, idx) => requestedNames.indexOf(n) !== idx);
  if (dupes.length > 0) throw new Error('requested_names: duplicates — ' + dupes.join(','));
  const collisions = requestedNames.filter(n => existingNames.includes(n));
  return { ok: collisions.length === 0, collisions };
}
function assertContainerNames(existing, requested) {
  const v = evaluateContainerNameUniqueness(existing, requested);
  if (!v.ok) throw Object.assign(new Error('CONTAINER NAMES: ' + (v.collisions||[]).join(',') + ' dup:' + (v.dupes||[]).join(',')), { name: 'ContainerNameCollision' });
  return v;
}

function makeRegistry(marker) {
  assertRunMarker(marker);
  return { marker, resources: new Set() };
}
function registerResource(reg, name) {
  if (typeof name !== 'string' || name.length === 0) throw new Error('resource name: empty');
  if (!name.includes(reg.marker)) throw new Error('resource name missing run marker: ' + name);
  reg.resources.add(name);
}
function isRegistered(reg, name) { return reg.resources.has(name); }
function ownershipRejectionReason(reg, name) {
  if (!reg || !reg.marker || !isRunMarker(reg.marker)) return 'bad_registry';
  if (typeof name !== 'string' || name.length === 0) return 'missing_name';
  if (!reg.resources.has(name)) return 'not_in_registry';
  return null;
}

function evaluateCleanup(deleted, expected, reg) {
  if (!Array.isArray(deleted)) throw new Error('deleted: must be array');
  if (!Array.isArray(expected)) throw new Error('expected: must be array');
  if (expected.length === 0) throw new Error('expected: empty — no cleanup to verify');
  const missing = expected.filter(n => !deleted.includes(n));
  const foreign = deleted.filter(n => !expected.includes(n));
  const notOwned = deleted.filter(n => reg && reg.resources && !reg.resources.has(n));
  return { ok: missing.length === 0 && foreign.length === 0 && notOwned.length === 0, missing, foreign, notOwned };
}
function evaluatePostRead(remaining, reg) {
  if (!reg) throw new Error('post_read: no registry');
  const rem = Array.isArray(remaining) ? remaining.filter(n => typeof n === 'string' && reg.resources.has(n)) : [];
  return { verified: rem.length === 0, remaining: rem };
}
function assertCleanupVerified(deleted, expected, reg, postRead) {
  const cl = evaluateCleanup(deleted, expected, reg);
  if (!cl.ok) throw Object.assign(new Error('CLEANUP FAILED: missing=' + cl.missing.join(',') + ' foreign=' + cl.foreign.join(',') + ' notOwned=' + cl.notOwned.join(',')), { name: 'CleanupFailed', detail: cl });
  if (postRead === undefined || postRead === null) throw Object.assign(new Error('CLEANUP UNVERIFIED: no post-read performed'), { name: 'CleanupUnverified' });
  const pr = evaluatePostRead(postRead, reg);
  if (!pr.verified) throw Object.assign(new Error('CLEANUP UNVERIFIED: post-read found remaining'), { name: 'CleanupUnverified', remaining: pr.remaining });
  return { cleanup: cl, postRead: pr };
}

function evaluateMarkerReadability(dbMarker, servedMarker, expectedMarker) {
  assertRunMarker(expectedMarker);
  if (typeof dbMarker !== 'string' || dbMarker.length === 0) return { ok: false, reason: 'db_marker_missing_or_empty' };
  if (typeof servedMarker !== 'string' || servedMarker.length === 0) return { ok: false, reason: 'served_marker_missing_or_empty' };
  if (dbMarker !== expectedMarker) return { ok: false, reason: dbMarker.indexOf(expectedMarker) === 0 ? 'db_prefix_collision' : dbMarker.endsWith(expectedMarker) ? 'db_suffix_collision' : 'db_mismatch' };
  if (servedMarker !== expectedMarker) return { ok: false, reason: servedMarker.indexOf(expectedMarker) === 0 ? 'served_prefix_collision' : servedMarker.endsWith(expectedMarker) ? 'served_suffix_collision' : 'served_mismatch' };
  return { ok: true };
}
function assertMarkerReadable(db, served, expected) {
  const v = evaluateMarkerReadability(db, served, expected);
  if (!v.ok) throw Object.assign(new Error('MARKER NOT READABLE: ' + v.reason), { name: 'MarkerNotReadable', reason: v.reason });
  return v;
}

module.exports = {
  newRunMarker, isRunMarker, assertRunMarker,
  requireString, requireArray, requireObject,
  evaluateDaemonTarget, assertDaemonTarget,
  evaluateImageAvailability, assertImages,
  evaluateContainerNameUniqueness, assertContainerNames,
  makeRegistry, registerResource, isRegistered, ownershipRejectionReason,
  evaluateCleanup, evaluatePostRead, assertCleanupVerified,
  evaluateMarkerReadability, assertMarkerReadable,
  MARKER_RE,
};
