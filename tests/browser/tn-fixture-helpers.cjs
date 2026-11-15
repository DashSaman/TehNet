'use strict';
/* TN-FIXTURE-HELPERS-QUALIFY-20261115 rev2 — corrections per MANAGER_REVIEW (comment 6901713229):
 * NEG1 redact actual tn_service_receipt (and tn_zp_receipt) query values;
 * NEG2 exact +marker@ email boundary in JS predicate AND generated PHP (no bare substring);
 * NEG3 cleanup verification: non-array discovery, incomplete/extra/failed deletion,
 *      post-cleanup re-read still finding owned records => FAILED_CLEANUP with evidence;
 *      generated PHP checks wp_delete_post's actual return before reporting deletion;
 * preflight now REQUIRES expected fixture identity (home_url) — a separate staging with
 * identical flags is rejected. No I/O; effects injected; tests stub everything. */

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

/* --- ownership predicate: EXACT +marker@ email boundary (fail closed) ---
 * The synthetic owned email is `<local>+<marker>@example.invalid`. Requiring the
 * '+',marker,'@' delimiters makes prefix collisions (marker+"x") impossible. */
function ownershipRejectionReason(rec, marker) {
  if (!isRunMarker(marker)) return 'bad_marker';
  if (!rec || typeof rec !== 'object' || Array.isArray(rec)) return 'not_object';
  if (!Number.isInteger(rec.id) || rec.id <= 0) return 'bad_id';
  if (!ALLOWED_TYPES.includes(rec.type)) return 'disallowed_type';
  const hasMarker = typeof rec.email === 'string'
    ? rec.email.indexOf('+' + marker + '@') !== -1
    : rec.email_has_marker === true; // PHP-side evidence uses the same +marker@ boundary
  if (!hasMarker) return 'email_marker_mismatch';
  return null;
}
function isOwnedRecord(rec, marker) {
  return ownershipRejectionReason(rec, marker) === null;
}

/* --- preflight verdict (fail closed; requires expected fixture identity) --- */
function evaluatePreflight(probes, expected) {
  const p = (probes && typeof probes === 'object') ? probes : {};
  const homeUrl = expected && typeof expected.home_url === 'string' ? expected.home_url : null;
  const checks = [
    ['fixture_identity', homeUrl !== null && p.home === homeUrl],
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
 * pre_wp_mail filter, which must return false for the probe value.
 * home_url() enables the expected-fixture-identity check. */
function buildPreflightProbePhp() {
  return '<?php\n' +
    '$env=(string)wp_get_environment_type();\n' +
    '$home=home_url("/");\n' +
    '$blog=(string)get_option("blog_public","1");\n' +
    '$mail_blocked=(apply_filters("pre_wp_mail",null,array())===false);\n' +
    '$http_blocked=(defined("WP_HTTP_BLOCK_EXTERNAL")&&WP_HTTP_BLOCK_EXTERNAL);\n' +
    '$cron_disabled=(defined("DISABLE_WP_CRON")&&DISABLE_WP_CRON);\n' +
    '$http_probe=is_wp_error(apply_filters("pre_http_request",false,array(),"https://example.invalid"));\n' +
    '$gws=apply_filters("woocommerce_available_payment_gateways",array("tn-guard-sentinel"=>"sentinel"));\n' +
    '$payments_disabled=(is_array($gws)&&count($gws)===0);\n' +
    'echo json_encode(array("env"=>$env,"home"=>$home,"blog_public"=>$blog,"mail_blocked"=>$mail_blocked,' +
    '"http_blocked"=>$http_blocked,"cron_disabled"=>$cron_disabled,"http_probe_blocked"=>$http_probe,' +
    '"payments_disabled"=>$payments_disabled));\n';
}
/* Find ALL records whose _tn_email contains the exact +marker@ token; verdict per record. */
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
    '"email_has_marker"=>(strpos($email,"+".$m."@")!==false));\n' +
    '}\n' +
    'echo json_encode($out);\n';
}
/* Delete ONLY ids passing the exact +marker@ comparison; wp_delete_post's actual
 * return is checked before reporting a deletion; everything else is preserved. */
function buildDeleteOwnedPhp(marker, ids) {
  assertRunMarker(marker);
  const m = phpSingleQuoted(marker);
  const list = phpIntList(ids);
  return '<?php\n' +
    '$m=' + m + ';\n' +
    '$allowed=array("tn_ticket","tn_quote");\n' +
    '$ids=' + list + ';\n' +
    '$deleted=array();$skipped=array();$failed=array();\n' +
    'foreach($ids as $id){\n' +
    '  $p=get_post($id);\n' +
    '  $email=($p)?(string)get_post_meta($id,"_tn_email",true):"";\n' +
    '  $owned=($p&&in_array($p->post_type,$allowed,true)&&strpos($email,"+".$m."@")!==false);\n' +
    '  if(!$owned){$skipped[]=(int)$id;continue;}\n' +
    '  $res=wp_delete_post($id,true);\n' +
    '  if($res!==false&&$res!==null){$deleted[]=(int)$id;}else{$failed[]=(int)$id;}\n' +
    '}\n' +
    'echo json_encode(array("deleted"=>$deleted,"skipped"=>$skipped,"failed"=>$failed));\n';
}

/* --- output serialization: real checks array bound + token redaction ---
 * Actual application params redacted: tn_service_receipt (service receipt token)
 * and tn_zp_receipt (payment receipt), plus generic token/key carriers. */
function redactText(value, marker) {
  if (typeof value !== 'string') return value;
  let out = value.split(marker).join('[REDACTED]');
  return out.replace(/([?&](?:tn_service_receipt|tn_zp_receipt|tn_token|token|key|tn_receipt)=)[^&]*/gi, '$1[REDACTED]');
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

/* --- journey orchestrator: preflight gate, finally-style cleanup, injected effects ---
 * Cleanup is VERIFIED, never trusted: delete-result completeness, no extras,
 * and a post-cleanup re-read must find zero owned records. */
async function runJourney(spec) {
  if (!spec || typeof spec !== 'object') throw new TypeError('runJourney: spec object required');
  const { marker, effects, operation } = spec;
  const expected = spec.expectedFixture;
  for (const k of ['preflightProbes', 'openBrowser', 'closeBrowser', 'findOwnedRecords', 'deleteOwnedRecords']) {
    if (typeof (effects && effects[k]) !== 'function') throw new TypeError('runJourney: effects.' + k + ' function required');
  }
  const log = [];
  const traced = (name, fn) => async (...a) => { log.push({ effect: name }); return fn(...a); };
  if (!isRunMarker(marker)) return { status: 'ABORTED_BAD_MARKER', effectLog: log };
  if (!expected || typeof expected.home_url !== 'string' || !expected.home_url) {
    return { status: 'ABORTED_BAD_SPEC', effectLog: log };
  }
  /* 1. read-only preflight — before ANY mutation; identity must match the expected fixture */
  const probes = await traced('preflightProbes', effects.preflightProbes)();
  const verdict = evaluatePreflight(probes, expected);
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
  /* 4. owned-only cleanup with verification; unowned records preserved untouched */
  const cleanup = { requested: 0, deleted: [], delete_failed_ids: [], skipped_unowned: [], post_read_owned_remaining: [], error: null };
  let found = null;
  try {
    found = await traced('findOwnedRecords', effects.findOwnedRecords)(marker);
  } catch (e) { cleanup.error = 'discovery_failed:' + e.message; }
  if (!cleanup.error && !Array.isArray(found)) cleanup.error = 'non_array_discovery';
  if (!cleanup.error) {
    const owned = found.filter(r => isOwnedRecord(r, marker));
    const unowned = found.filter(r => !isOwnedRecord(r, marker));
    cleanup.requested = owned.length;
    cleanup.skipped_unowned = unowned.map(r => ({
      id: r && Number.isInteger(r.id) ? r.id : null,
      type: r && r.type,
      reason: ownershipRejectionReason(r, marker),
    }));
    if (owned.length) {
      let del = null;
      try {
        del = await traced('deleteOwnedRecords', effects.deleteOwnedRecords)(owned.map(r => r.id), marker);
      } catch (e) { cleanup.error = 'delete_failed:' + e.message; }
      if (del && typeof del === 'object') {
        const deletedIds = Array.isArray(del.deleted) ? del.deleted : null;
        const failedIds = Array.isArray(del.failed) ? del.failed : [];
        const skippedIds = Array.isArray(del.skipped) ? del.skipped : [];
        cleanup.deleted = Array.isArray(deletedIds) ? deletedIds : [];
        cleanup.delete_failed_ids = failedIds;
        if (!Array.isArray(deletedIds)) cleanup.error = 'delete_result_malformed';
        const wanted = owned.map(r => r.id);
        const missing = wanted.filter(id => !cleanup.deleted.includes(id));
        const extras = cleanup.deleted.filter(id => !wanted.includes(id));
        if (!cleanup.error && missing.length) cleanup.error = 'incomplete_deletion:' + missing.join(',');
        if (!cleanup.error && extras.length) cleanup.error = 'extra_deletion:' + extras.join(',');
        if (!cleanup.error && skippedIds.some(id => wanted.includes(id))) cleanup.error = 'requested_id_skipped';
        /* post-cleanup re-read: owned records must be gone */
        if (!cleanup.error) {
          let after = null;
          try { after = await traced('findOwnedRecords', effects.findOwnedRecords)(marker); }
          catch (e) { cleanup.error = 'post_read_failed:' + e.message; }
          if (Array.isArray(after)) {
            const remaining = after.filter(r => isOwnedRecord(r, marker)).map(r => r.id);
            cleanup.post_read_owned_remaining = remaining;
            if (remaining.length) cleanup.error = 'owned_still_present:' + remaining.join(',');
          }
        }
      } else if (!cleanup.error) cleanup.error = 'delete_result_missing';
    }
  }
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
