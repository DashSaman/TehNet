'use strict';
/* TN-SYNTHETIC-BOOTSTRAP-20261117 rev4 — PREDICATE_CONTRACT_DRAFT / BOOTSTRAP_LIFECYCLE_NOT_IMPLEMENTED
 * Corrections per MANAGER_REVIEW 6945979322 + 6947347938 (semantic fixes A-D, evidence F).
 * SOURCE_ONLY / INTEGRATION_NOT_RUN. Pure predicates with strict input validation.
 * All previous title-equality/base-attribution/P2-driver-row corrections preserved. */

const MARKER_RE = /^TN-SYN-[0-9a-z]{6,}-[0-9a-z]{6,}$/;

function newRunMarker(nowMs, rngValue) {
  const t = Number.isFinite(nowMs) ? Math.floor(nowMs) : Date.now();
  const rng = Number.isFinite(rngValue) ? Math.max(0, Math.min(1, rngValue)) : Math.random();
  const suffix = Math.floor(rng * 1296 ** 3).toString(36).padStart(6, '0').slice(0, 6);
  return 'TN-SYN-' + t.toString(36).padStart(6, '0') + '-' + suffix;
}
function isRunMarker(v) { return typeof v === 'string' && MARKER_RE.test(v); }
function assertRunMarker(v) { if (!isRunMarker(v)) throw new Error('invalid run marker: ' + String(v).slice(0, 60)); return v; }
function requireString(v, label) { if (typeof v !== 'string' || v.trim().length === 0) throw new Error(label + ': missing or empty'); return v.trim(); }
function requireArray(v, label) { if (!Array.isArray(v)) throw new Error(label + ': must be an array'); if (v.length === 0) throw new Error(label + ': must be non-empty'); return v; }
function requireObject(v, label) { if (!v || typeof v !== 'object' || Array.isArray(v)) throw new Error(label + ': missing or not object'); return v; }

/* A: daemon target — structural parse; reject conflicting/unresolved context+Host */
function evaluateDaemonTarget(info) {
  requireObject(info, 'daemon_info');
  let hasEndpoint = false, hasHost = false, epFromEndpoints = null, epFromHost = null;
  if (info.Endpoints && typeof info.Endpoints === 'object' &&
      info.Endpoints.docker && typeof info.Endpoints.docker === 'object' &&
      typeof info.Endpoints.docker.Host === 'string' && info.Endpoints.docker.Host.length > 0) {
    epFromEndpoints = info.Endpoints.docker.Host; hasEndpoint = true;
  }
  if (typeof info.Host === 'string' && info.Host.length > 0) { epFromHost = info.Host; hasHost = true; }
  if (hasEndpoint && hasHost && epFromEndpoints !== epFromHost)
    throw new Error('DAEMON: conflicting endpoint sources — "' + epFromEndpoints + '" vs "' + epFromHost + '"');
  const ep = epFromEndpoints || epFromHost;
  if (!ep) throw new Error('DAEMON: no effective endpoint observed (name/context alone insufficient)');
  const npipeLocal = /^npipe:\/\/\/\/\.\/pipe\/docker(_engine|DesktopLinuxEngine)?$/.test(ep) || ep === 'npipe:////./pipe/docker_engine';
  const unixSock = ep === 'unix:///var/run/docker.sock';
  const tcpLocal = /^tcp:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(ep);
  if (!npipeLocal && !unixSock && !tcpLocal) {
    throw new Error('DAEMON: endpoint "' + ep + '" is not a permitted owner-local target');
  }
  return { ok: true, endpoint: ep, type: npipeLocal ? 'npipe' : unixSock ? 'unix' : 'tcp_local' };
}
function assertDaemonTarget(info) {
  const v = evaluateDaemonTarget(info);
  if (!v.ok) throw Object.assign(new Error('DAEMON BLOCKED: ' + (v.failed || []).join(',')), { name: 'DaemonBlocked', failed: v.failed });
  return v;
}

/* D: image availability — pinned expected IDs vs observed inspection results with full sha256 comparison */
function evaluateImageAvailability(requiredImages, observedInspections) {
  requireArray(requiredImages, 'required_images');
  if (requiredImages.length === 0) throw new Error('required_images: empty array');
  // Every entry MUST be {name, expected_id} with BOTH fields — name-only/unpinned/null/42 reject
  const expected_map = {};
  for (const entry of requiredImages) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry))
      throw new Error('required_images: invalid entry (must be {name, expected_id} object), got: ' + JSON.stringify(entry));
    if (typeof entry.name !== 'string' || entry.name.trim().length === 0)
      throw new Error('required_images: missing or empty name');
    if (typeof entry.expected_id !== 'string' || !/^sha256:[0-9a-f]{64}$/.test(entry.expected_id))
      throw new Error('required_images: missing or invalid expected_id (must be sha256:<64hex>) for ' + entry.name);
    if (expected_map[entry.name]) throw new Error('required_images: duplicate entry for ' + entry.name);
    expected_map[entry.name] = entry.expected_id;
  }
  if (!observedInspections || typeof observedInspections !== 'object' || Array.isArray(observedInspections))
    return { ok: false, missing: Object.keys(expected_map), mismatches: [], observed_ids: {} };
  const missing = [], mismatches = [], observed_ids = {};
  for (const img of Object.keys(expected_map)) {
    const obs = observedInspections[img];
    if (!obs || typeof obs !== 'object' || obs.exit !== 0 || obs.inspected !== true ||
        typeof obs.id !== 'string' || !/^sha256:[0-9a-f]{64}$/.test(obs.id))
      { missing.push(img); continue; }
    const expected_id = expected_map[img];
    if (obs.id !== expected_id) {
      mismatches.push({ image: img, expected: expected_id, observed: obs.id }); continue;
    }
    observed_ids[img] = obs.id;
  }
  return { ok: missing.length === 0 && mismatches.length === 0, missing, mismatches, observed_ids };
}
function assertImages(required, observed) {
  const v = evaluateImageAvailability(required, observed);
  if (!v.ok) {
    const details = (v.missing || []).join(',') + ((v.mismatches || []).length > 0 ? ' mismatches:' + JSON.stringify(v.mismatches) : '');
    throw Object.assign(new Error('IMAGE BLOCKED: ' + details), { name: 'ImageBlocked', missing: v.missing, mismatches: v.mismatches });
  }
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

/* C: plan-based registry — structured identity evidence, not just any string */
function makePlan(marker, resourceNames) {
  assertRunMarker(marker);
  requireArray(resourceNames, 'resource_names');
  const plan = { marker, resources: {}, expected_bindings: {} };
  for (const n of resourceNames) {
    if (typeof n !== 'string' || n.length === 0) throw new Error('plan: empty resource name');
    if (!n.includes(marker)) throw new Error('plan: resource name missing run marker — ' + n);
    plan.resources[n] = { registered: true, identity_verified: false, identity_evidence: null };
    plan.expected_bindings[n] = null;
  }
  return plan;
}
/* verifyIdentity: structured binding — resource name, observed container ID, and plan marker must all match */
function verifyIdentity(plan, resourceName, observedBinding) {
  const b = requireObject(observedBinding, 'observed_binding');
  const containerId = requireString(b.container_id, 'observed_binding.container_id');
  const observedRunMarker = requireString(b.run_marker, 'observed_binding.run_marker');
  if (!plan.resources[resourceName]) throw new Error('resource not in plan: ' + resourceName);
  const expected = plan.expected_bindings[resourceName];
  if (!expected || typeof expected !== 'object') throw new Error('identity_binding: no expected binding declared for ' + resourceName);
  if (observedRunMarker !== plan.marker) throw new Error('identity_binding: run_marker mismatch — observed "' + observedRunMarker + '" does not match plan marker "' + plan.marker + '"');
  if (containerId !== expected.container_id) throw new Error('identity_binding: container_id mismatch — observed "' + containerId + '" vs expected "' + expected.container_id + '"');
  if (containerId.length < 12) throw new Error('identity_binding.container_id: too short');
  plan.resources[resourceName].identity_verified = true;
  plan.resources[resourceName].identity_evidence = { container_id: containerId, run_marker: observedRunMarker };
}
function setExpectedBinding(plan, resourceName, containerId) {
  if (!plan.resources[resourceName]) throw new Error('resource not in plan: ' + resourceName);
  if (typeof containerId !== 'string' || containerId.length < 12) throw new Error('container_id: missing or too short');
  plan.expected_bindings[resourceName] = { container_id: containerId, run_marker: plan.marker };
}
function setExpectedBinding(plan, resourceName, containerId) {
  if (!plan.resources[resourceName]) throw new Error('resource not in plan: ' + resourceName);
  if (typeof containerId !== 'string' || containerId.length < 12) throw new Error('container_id: missing or too short');
  plan.expected_bindings[resourceName] = { container_id: containerId, run_marker: plan.marker };
}
function isRegistered(plan, name) {
  return plan && plan.resources && typeof plan.resources[name] === 'object';
}
/* ownership: requires identity_verified=true, not just name presence */
function ownershipRejectionReason(plan, name) {
  if (!plan || !plan.marker || !isRunMarker(plan.marker)) return 'bad_plan';
  if (typeof name !== 'string' || name.length === 0) return 'missing_name';
  const r = plan.resources[name];
  if (!r) return 'not_in_plan';
  if (!r.identity_verified) return 'identity_not_verified';
  return null;
}

/* cleanup: every deleted item must pass the shared ownership verdict; reject duplicates, inherited keys */
function evaluateCleanup(deleted, expected, plan) {
  if (!Array.isArray(deleted)) throw new Error('deleted: must be array');
  if (!Array.isArray(expected)) throw new Error('expected: must be array');
  if (expected.length === 0) throw new Error('expected: empty — no cleanup to verify');
  const dupDel = deleted.filter((n, idx) => deleted.indexOf(n) !== idx);
  if (dupDel.length > 0) throw new Error('deleted: duplicate entries — ' + dupDel.join(','));
  const dupExp = expected.filter((n, idx) => expected.indexOf(n) !== idx);
  if (dupExp.length > 0) throw new Error('expected: duplicate entries — ' + dupExp.join(','));
  for (const n of [...deleted, ...expected]) {
    if (n === 'constructor' || n === '__proto__' || n === 'toString' || n === 'hasOwnProperty')
      throw new Error('inherited prototype key rejected: ' + n);
  }
  const missing = expected.filter(n => !deleted.includes(n));
  const foreign = deleted.filter(n => !expected.includes(n));
  const notOwned = deleted.filter(n => ownershipRejectionReason(plan, n) !== null);
  return { ok: missing.length === 0 && foreign.length === 0 && notOwned.length === 0, missing, foreign, notOwned };
}

/* B: post-read — validate every entry before filtering; reject wrong-run/failed/malformed; never coerce to empty */
function evaluatePostRead(remaining, plan) {
  if (!plan || !plan.marker || !isRunMarker(plan.marker)) throw new Error('post_read: invalid plan');
  if (!remaining || typeof remaining !== 'object' || Array.isArray(remaining))
    throw new Error('post_read: malformed — must be {success:true, remaining:[...]}');
  if (remaining.success !== true) throw new Error('post_read: read failure — success flag not true');
  if (!Array.isArray(remaining.remaining)) throw new Error('post_read: remaining must be an array');
  for (const n of remaining.remaining) {
    if (typeof n !== 'string') throw new Error('post_read: non-string remaining entry');
    if (!plan.resources[n]) throw new Error('post_read: remaining entry not in plan: ' + n);
  }
  const owned_remaining = remaining.remaining.filter(n => typeof n === 'string' && plan.resources[n]);
  return { verified: owned_remaining.length === 0, remaining: owned_remaining };
}
function assertCleanupVerified(deleted, expected, plan, postRead) {
  const cl = evaluateCleanup(deleted, expected, plan);
  if (!cl.ok) throw Object.assign(new Error('CLEANUP FAILED: missing=' + cl.missing.join(',') + ' foreign=' + cl.foreign.join(',') + ' notOwned=' + cl.notOwned.join(',')), { name: 'CleanupFailed', detail: cl });
  if (postRead === undefined || postRead === null)
    throw Object.assign(new Error('CLEANUP UNVERIFIED: no post-read performed'), { name: 'CleanupUnverified' });
  const pr = evaluatePostRead(postRead, plan);
  if (!pr.verified) throw Object.assign(new Error('CLEANUP UNVERIFIED: post-read found remaining=' + pr.remaining.join(',')), { name: 'CleanupUnverified', remaining: pr.remaining });
  return { cleanup: cl, postRead: pr };
}

/* marker readability: exact comparison of named/endpoint-bound fields */
function evaluateMarkerReadability(dbMarkerField, servedMarkerField, expectedMarker) {
  assertRunMarker(expectedMarker);
  if (typeof dbMarkerField !== 'string' || dbMarkerField.length === 0) return { ok: false, reason: 'db_marker_missing_or_empty' };
  if (typeof servedMarkerField !== 'string' || servedMarkerField.length === 0) return { ok: false, reason: 'served_marker_missing_or_empty' };
  if (dbMarkerField !== expectedMarker) return { ok: false, reason: dbMarkerField.indexOf(expectedMarker) === 0 ? 'db_prefix_collision' : dbMarkerField.endsWith(expectedMarker) ? 'db_suffix_collision' : 'db_mismatch' };
  if (servedMarkerField !== expectedMarker) return { ok: false, reason: servedMarkerField.indexOf(expectedMarker) === 0 ? 'served_prefix_collision' : servedMarkerField.endsWith(expectedMarker) ? 'served_suffix_collision' : 'served_mismatch' };
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
  makePlan, verifyIdentity, isRegistered, ownershipRejectionReason, setExpectedBinding,
  evaluateCleanup, evaluatePostRead, assertCleanupVerified,
  evaluateMarkerReadability, assertMarkerReadable,
  MARKER_RE,
};
