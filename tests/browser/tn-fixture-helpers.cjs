'use strict';
/* TN-FIXTURE-HELPERS-QUALIFY-20261115 — small pure helpers for run ownership + preflight.
 * No I/O, no SSH, no DB, no browser. External effects are injected by the caller
 * (runJourney spec.effects) so tests can stub everything.
 * Ownership rule: a record is owned iff its _tn_email contains the EXACT run marker.
 * No ID thresholds, no "newest record", no global transient cleanup. */

const MARKER_RE = /^TN-RUN-[0-9a-z]{4,}-[0-9a-z]{4,}$/;
const ALLOWED_TYPES = ['tn_ticket', 'tn_quote'];

/* --- run marker --- */
function newRunMarker(nowMs) {
  const t = Number.isFinite(nowMs) ? nowMs : Date.now();
  const r = Math.floor(Math.random() * 1296 ** 3).toString(36).padStart(3, '0');
  return 'TN-RUN-' + t.toString(36) + '-' + r;
}
function isRunMarker(v) {
  return typeof v === 'string' && MARKER_RE.test(v);
}
function assertRunMarker(v) {
  if (!isRunMarker(v)) throw new Error('invalid run marker: ' + String(v).slice(0, 40));
  return v;
}

/* The SAME marker reaches every form: service form, B2B form, no-JS form. */
function formEmail(marker, local) {
  assertRunMarker(marker);
  const l = typeof local === 'string' && local.length > 0 ? local : 'acceptance-test';
  return l + '+' + marker + '@example.invalid';
}

/* --- ownership predicate (exact marker containment; fail closed) --- */
function ownershipRejectionReason(rec, marker) {
  if (!isRunMarker(marker)) return 'bad_marker';
  if (!rec || typeof rec !== 'object' || Array.isArray(rec)) return 'not_object';
  if (!Number.isInteger(rec.id) || rec.id <= 0) return 'bad_id';
  if (!ALLOWED_TYPES.includes(rec.type)) return 'disallowed_type';
  const hasMarker = typeof rec.email === 'string'
    ? rec.email.indexOf(marker) !== -1
    : rec.email_has_marker === true;
  if (!hasMarker) return 'email_marker_mismatch';
  return null;
}
function isOwnedRecord(rec, marker) {
  return ownershipRejectionReason(rec, marker) === null;
}

/* --- preflight verdict (fail closed on any missing/undefined evidence) --- */
function evaluatePreflight(probes) {
  const p = (probes && typeof probes === 'object') ? probes : {};
  const checks = [
    ['env_staging', p.env === 'staging'],
    ['blog_public_0', p.blog_public === '0'],
    ['mail_block_confirmed', p.mail_blocked === true],
    ['http_block_confirmed', p.http_blocked === true],
    ['cron_disabled', p.cron_disabled === true],
    ['http_probe_blocked', p.http_probe_blocked === true],
    ['payments_disabled', p.payments_disabled === true],
  ];
  const failed = checks.filter(c => !c[1]).map(c => c[0]);
  return { ok: failed.length === 0, failed, checks: checks.map(([name, pass]) => ({ name, pass })) };
}
function assertPreflight(verdict) {
  if (!verdict || verdict.ok !== true) {
    const failed = verdict && Array.isArray(verdict.failed) ? verdict.failed.join(',') : 'unknown';
    const err = new Error('PREFLIGHT BLOCKED: ' + failed);
    err.name = 'PreflightBlocked';
    err.failed = verdict && verdict.failed;
    throw err;
  }
  return verdict;
}

/* --- generated PHP (real PHP string comparison; no JS syntax, no env vars) --- */
function phpSingleQuoted(v) {
  if (typeof v !== 'string' || v.length === 0) throw new TypeError('phpSingleQuoted: non-empty string required');
  if (/[\0\r\n]/.test(v)) throw new TypeError('phpSingleQuoted: control/newline chars not allowed');
  return "'" + v.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";
}
function phpIntList(ids) {
  const list = (Array.isArray(ids) ? ids : []).map(x => Number(x));
  for (const x of list) {
    if (!Number.isInteger(x) || x <= 0) throw new TypeError('phpIntList: positive integers only');
  }
  return 'array(' + list.join(',') + ')';
}
/* Read-only probe — mirrors ops/migrate-growth-content.php isolation guard.
 * Does NOT call wp_mail (no send attempt): block is evidenced by the installed
 * pre_wp_mail filter, which must return false for the probe value. */
function buildPreflightProbePhp() {
  return '<?php\n' +
    '$env=(string)wp_get_environment_type();\n' +
    '$blog=(string)get_option("blog_public","1");\n' +
    '$mail_blocked=(apply_filters("pre_wp_mail",null,array())===false);\n' +
    '$http_blocked=(defined("WP_HTTP_BLOCK_EXTERNAL")&&WP_HTTP_BLOCK_EXTERNAL);\n' +
    '$cron_disabled=(defined("DISABLE_WP_CRON")&&DISABLE_WP_CRON);\n' +
    '$http_probe=is_wp_error(apply_filters("pre_http_request",false,array(),"https://example.invalid"));\n' +
    '$gws=apply_filters("woocommerce_available_payment_gateways",array("tn-guard-sentinel"=>"sentinel"));\n' +
    '$payments_disabled=(is_array($gws)&&count($gws)===0);\n' +
    'echo json_encode(array("env"=>$env,"blog_public"=>$blog,"mail_blocked"=>$mail_blocked,' +
    '"http_blocked"=>$http_blocked,"cron_disabled"=>$cron_disabled,"http_probe_blocked"=>$http_probe,' +
    '"payments_disabled"=>$payments_disabled));\n';
}
/* Find ALL records whose _tn_email contains the exact marker; verdict per record. */
function buildFindOwnedPhp(marker) {
  assertRunMarker(marker);
  const m = phpSingleQuoted(marker);
  return '<?php\n' +
    '$m=' + m + ';\n' +
    '$q=new WP_Query(array("post_type"=>array("tn_ticket","tn_quote"),"post_status"=>"any",' +
    '"posts_per_page"=>50,"orderby"=>"ID","order"=>"DESC",' +
    '"meta_query"=>array(array("key"=>"_tn_email","value"=>$m,"compare"=>"LIKE"))));\n' +
    '$out=array();\n' +
    'foreach($q->posts as $p){\n' +
    '  $email=(string)get_post_meta($p->ID,"_tn_email",true);\n' +
    '  $out[]=array("id"=>(int)$p->ID,"type"=>$p->post_type,"status"=>$p->post_status,' +
    '"email_has_marker"=>(strpos($email,$m)!==false));\n' +
    '}\n' +
    'echo json_encode($out);\n';
}
/* Delete ONLY ids that pass the server-side exact-marker comparison; rest preserved. */
function buildDeleteOwnedPhp(marker, ids) {
  assertRunMarker(marker);
  const m = phpSingleQuoted(marker);
  const list = phpIntList(ids);
  return '<?php\n' +
    '$m=' + m + ';\n' +
    '$allowed=array("tn_ticket","tn_quote");\n' +
    '$ids=' + list + ';\n' +
    '$deleted=array();$skipped=array();\n' +
    'foreach($ids as $id){\n' +
    '  $p=get_post($id);\n' +
    '  $email=($p)?(string)get_post_meta($id,"_tn_email",true):"";\n' +
    '  $owned=($p&&in_array($p->post_type,$allowed,true)&&strpos($email,$m)!==false);\n' +
    '  if($owned){wp_delete_post($id,true);$deleted[]=(int)$id;}else{$skipped[]=(int)$id;}\n' +
    '}\n' +
    'echo json_encode(array("deleted"=>$deleted,"skipped"=>$skipped));\n';
}

/* --- output serialization: real checks array bound + token redaction --- */
function redactText(value, marker) {
  if (typeof value !== 'string') return value;
  let out = value.split(marker).join('[REDACTED]');
  return out.replace(/([?&](?:tn_token|token|key|tn_receipt)=)[^&]*/gi, '$1[REDACTED]');
}
function serializeOutput(out, checks, marker) {
  assertRunMarker(marker);
  const copy = JSON.parse(JSON.stringify(out));
  copy.checks = JSON.parse(JSON.stringify(checks || []));
  const walk = node => {
    for (const k of Object.keys(node)) {
      const v = node[k];
      if (typeof v === 'string') node[k] = redactText(v, marker);
      else if (v && typeof v === 'object') walk(v);
    }
  };
  walk(copy);
  return copy;
}

/* --- journey orchestrator: preflight gate, finally-style cleanup, injected effects --- */
async function runJourney(spec) {
  if (!spec || typeof spec !== 'object') throw new TypeError('runJourney: spec object required');
  const { marker, effects, operation } = spec;
  for (const k of ['preflightProbes', 'openBrowser', 'closeBrowser', 'findOwnedRecords', 'deleteOwnedRecords']) {
    if (typeof (effects && effects[k]) !== 'function') throw new TypeError('runJourney: effects.' + k + ' function required');
  }
  const log = [];
  const traced = (name, fn) => async (...a) => { log.push({ effect: name }); return fn(...a); };
  if (!isRunMarker(marker)) return { status: 'ABORTED_BAD_MARKER', effectLog: log };
  /* 1. read-only preflight — before ANY mutation */
  const probes = await traced('preflightProbes', effects.preflightProbes)();
  const verdict = evaluatePreflight(probes);
  if (!verdict.ok) return { status: 'ABORTED_PREFLIGHT', verdict, effectLog: log };
  /* 2. browser + operation; any throw still reaches cleanup */
  let browser = null, opened = false, operationError = null, operationResult = null, closeError = null;
  try {
    browser = await traced('openBrowser', effects.openBrowser)();
    opened = true;
    if (typeof operation === 'function') {
      operationResult = await operation({
        browser,
        submitForm: effects.submitForm
          ? traced('submitForm', effects.submitForm)
          : undefined,
      });
    }
  } catch (e) { operationError = e; }
  /* 3. browser ALWAYS closed */
  if (opened) {
    try { await traced('closeBrowser', effects.closeBrowser)(browser); }
    catch (e) { closeError = e; }
  }
  /* 4. owned-only cleanup; unowned records preserved untouched */
  const cleanup = { requested: 0, deleted: [], skipped_unowned: [], error: null };
  try {
    const found = await traced('findOwnedRecords', effects.findOwnedRecords)(marker);
    const all = Array.isArray(found) ? found : [];
    const owned = all.filter(r => isOwnedRecord(r, marker));
    const unowned = all.filter(r => !isOwnedRecord(r, marker));
    cleanup.requested = owned.length;
    cleanup.skipped_unowned = unowned.map(r => ({
      id: r && Number.isInteger(r.id) ? r.id : null,
      type: r && r.type,
      reason: ownershipRejectionReason(r, marker),
    }));
    const del = await traced('deleteOwnedRecords', effects.deleteOwnedRecords)(owned.map(r => r.id), marker);
    cleanup.deleted = (del && Array.isArray(del.deleted)) ? del.deleted : [];
  } catch (e) { cleanup.error = e.message; }
  /* 5. verdict: cleanup failure is a FAILED result, never silent success */
  let status;
  if (operationError) status = 'FAILED_OPERATION';
  else if (cleanup.error || closeError) status = 'FAILED_CLEANUP';
  else status = 'PASSED';
  return {
    status,
    operationError: operationError ? operationError.message : null,
    closeError: closeError ? closeError.message : null,
    cleanup,
    operationResult,
    effectLog: log,
  };
}

module.exports = {
  newRunMarker, isRunMarker, assertRunMarker, formEmail,
  isOwnedRecord, ownershipRejectionReason,
  evaluatePreflight, assertPreflight,
  phpSingleQuoted, phpIntList,
  buildPreflightProbePhp, buildFindOwnedPhp, buildDeleteOwnedPhp,
  redactText, serializeOutput, runJourney, ALLOWED_TYPES,
};
