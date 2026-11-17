'use strict';
/* TN-SYNTHETIC-BOOTSTRAP-20261117 rev3 — PREDICATE_CONTRACT_DRAFT / BOOTSTRAP_LIFECYCLE_NOT_IMPLEMENTED
 * Corrections per MANAGER_REVIEW 6945979322 (all four remaining gate failures + evidence precision).
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

/* --- A: daemon target — structural parse of effective endpoint, not substring match --- */
/* Permitted owner-local endpoints: npipe docker_engine pipes + unix docker.sock + tcp localhost/127.0.0.1 only */
function evaluateDaemonTarget(info) {
  requireObject(info, 'daemon_info');
  // resolve effective endpoint: Endpoints.docker.Host > Host > endpoint (priority order)
  let ep = null;
  if (info.Endpoints && typeof info.Endpoints === 'object' &&
      info.Endpoints.docker && typeof info.Endpoints.docker === 'object' &&
      typeof info.Endpoints.docker.Host === 'string' && info.Endpoints.docker.Host.length > 0) {
    ep = info.Endpoints.docker.Host;
  } else if (typeof info.Host === 'string' && info.Host.length > 0) {
    ep = info.Host;
  } else if (typeof info.endpoint === 'string' && info.endpoint.length > 0) {
    ep = info.endpoint;
  }
  if (!ep) throw new Error('DAEMON: no effective endpoint observed (name/context alone insufficient)');
  // structural parse: must match one of the permitted owner-local patterns exactly
  const npipeLocal = /^npipe:\/{2,}\.\/pipe\/docker(DesktopLinux)?Engine$/.test(ep);
  const unixSock = ep === 'unix:///var/run/docker.sock';
  const tcpLocal = /^tcp:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(ep);
  if (!npipeLocal && !unixSock && !tcpLocal) {
    throw new Error('DAEMON: endpoint "' + ep + '" is not a permitted owner-local target — remote/unrecognized schemes and non-local hostnames rejected');
  }
  return { ok: true, endpoint: ep, type: npipeLocal ? 'npipe' : unixSock ? 'unix' : 'tcp_local' };
}
function assertDaemonTarget(info) {
  const v = evaluateDaemonTarget(info);
  if (!v.ok) throw Object.assign(new Error('DAEMON BLOCKED: ' + (v.failed || []).join(',')), { name: 'DaemonBlocked', failed: v.failed });
  return v;
}

/* --- B: image availability — pinned required identities + observed inspection with valid sha256 digest --- */
function evaluateImageAvailability(requiredImages, observedInspections) {
  requireArray(requiredImages, 'required_images');
  for (const img of requiredImages) {
    if (typeof img !== 'string' || img.trim().length === 0) throw new Error('required_images: empty entry');
  }
  // observedInspections must be an object keyed by image name with {exit, inspected, id}
  if (!observedInspections || typeof observedInspections !== 'object' || Array.isArray(observedInspections))
    return { ok: false, missing: requiredImages.slice(), observed_ids: {}, unobserved: requiredImages.slice() };
  const missing = [];
  const observed_ids = {};
  const failed_inspection = [];
  for (const img of requiredImages) {
    const obs = observedInspections[img];
    if (!obs || typeof obs !== 'object' || obs.exit !== 0 || obs.inspected !== true ||
        typeof obs.id !== 'string' || !/^sha256:[0-9a-f]{64}$/.test(obs.id))
      missing.push(img);
    else observed_ids[img] = obs.id;
  }
  return { ok: missing.length === 0, missing, observed_ids, failed_inspection };
}
function assertImages(required, observed) {
  const v = evaluateImageAvailability(required, observed);
  if (!v.ok) throw Object.assign(new Error('IMAGE BLOCKED: missing/failed ' + v.missing.join(',')), { name: 'ImageBlocked', missing: v.missing });
  return v;
}

/* --- container name uniqueness — strict --- */
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

/* --- C: registry — exact predeclared run plan, NOT substring ownership --- */
/* makePlan creates the authoritative predeclared resource set from the bootstrap plan */
function makePlan(marker, resourceNames) {
  assertRunMarker(marker);
  requireArray(resourceNames, 'resource_names');
  const plan = { marker, resources: {} };
  for (const n of resourceNames) {
    if (typeof n !== 'string' || n.length === 0) throw new Error('plan: empty resource name');
    if (!n.includes(marker)) throw new Error('plan: resource name missing run marker — ' + n);
    plan.resources[n] = { registered: true, identity_verified: false, owner_evidence: null };
  }
  return plan;
}
/* verifyIdentity must be called with independently supplied owner evidence (not just the name) */
function verifyIdentity(plan, resourceName, ownerEvidence) {
  if (!plan.resources[resourceName]) throw new Error('resource not in plan: ' + resourceName);
  if (typeof ownerEvidence !== 'string' || ownerEvidence.length === 0) throw new Error('owner_evidence: missing');
  plan.resources[resourceName].identity_verified = true;
  plan.resources[resourceName].owner_evidence = ownerEvidence;
}
/* admission: only exact plan-registered + identity-verified resources pass */
function ownershipRejectionReason(plan, name) {
  if (!plan || !plan.marker || !isRunMarker(plan.marker)) return 'bad_plan';
  if (typeof name !== 'string' || name.length === 0) return 'missing_name';
  const r = plan.resources[name];
  if (!r) return 'not_in_plan';
  if (!r.identity_verified) return 'identity_not_verified';
  return null;
}
function isRegistered(plan, name) {
  return plan && plan.resources && typeof plan.resources[name] === 'object';
}

/* --- cleanup: exact registry membership + post-read separ
ation — exact plan membership + post-read must be explicitly successful */
function evaluateCleanup(deleted, expected, plan) {
  if (!Array.isArray(deleted)) throw new Error('deleted: must be array');
  if (!Array.isArray(expected)) throw new Error('expected: must be array');
  if (expected.length === 0) throw new Error('expected: empty — no cleanup to verify');
  const missing = expected.filter(n => !deleted.includes(n));
  const foreign = deleted.filter(n => !expected.includes(n));
  const notOwned = deleted.filter(n => !plan || !plan.resources || !plan.resources[n]);
  return { ok: missing.length === 0 && foreign.length === 0 && notOwned.length === 0, missing, foreign, notOwned };
}
function evaluatePostRead(remaining, plan) {
  if (!plan || !plan.marker) throw new Error('post_read: no plan');
  if (!remaining || typeof remaining !== 'object' || Array.isArray(remaining))
    throw new Error('post_read: malformed — must be {success:true, remaining:[...]}');
  if (remaining.success !== true) throw new Error('post_read: read failure');
  if (!Array.isArray(remaining.remaining)) throw new Error('post_read: remaining must be array');
  const owned_remaining = remaining.remaining.filter(n => typeof n === 'string' && plan.resources[n]);
  return { verified: owned_remaining.length === 0, remaining: owned_remaining };
}
function assertCleanupVerified(deleted, expected, plan, postRead) {
  const cl = evaluateCleanup(deleted, expected, plan);
  if (!cl.ok) throw Object.assign(new Error('CLEANUP FAILED: missing=' + cl.missing.join(',') + ' foreign=' + cl.foreign.join(',') + ' notOwned=' + cl.notOwned.join(',')), { name: 'CleanupFailed', detail: cl });
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
  makePlan, verifyIdentity, isRegistered, ownershipRejectionReason,
  evaluateCleanup, evaluatePostRead, assertCleanupVerified,
  evaluateMarkerReadability, assertMarkerReadable,
  MARKER_RE,
};
