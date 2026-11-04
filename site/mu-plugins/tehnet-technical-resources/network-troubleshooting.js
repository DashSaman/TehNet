(function () {
  'use strict';
  const issueKeys = ['internet', 'dns', 'dhcp', 'vpn', 'vlan', 'nat', 'gateway'];
  const scopes = {unknown: 'هنوز مشخص نیست', one: 'یک دستگاه مشاهده شده', several: 'چند دستگاه یا یک بخش', widespread: 'چند بخش یا شعبه مشاهده شده'};
  const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);

  function buildReport(model, answers) {
    if (!issueKeys.includes(answers.problem) || !own(model, answers.problem)) throw new Error('Choose a known problem');
    const rule = model[answers.problem];
    const observation = own(rule.observations, answers.observation) ? answers.observation : 'unknown';
    const scope = own(scopes, answers.scope) ? answers.scope : 'unknown';
    const selected = rule.observations[observation];
    return {schema: 1, rulesVersion: '2026-11-04-v1', status: 'MANUAL_UNVERIFIED',
      problem: answers.problem, problemLabel: rule.title, scope, scopeLabel: scopes[scope],
      observation, observationLabel: selected.label, suggestedCheck: rule.test, reason: rule.why,
      nextReview: selected.advice, source: rule.source,
      limits: 'گزارش انتخاب دستی است؛ اندازه‌گیری، تشخیص قطعی یا ثبت تیکت نیست. هیچ فرمانی اجرا نشده است.'};
  }
  function summary(report) {
    return ['خلاصهٔ دستی عیب‌یابی شبکه', 'نشانه: ' + report.problemLabel, 'دامنهٔ مشاهده: ' + report.scopeLabel,
      'شاهد انتخاب‌شده: ' + report.observationLabel, 'بررسی پیشنهادی: ' + report.suggestedCheck,
      'دلیل: ' + report.reason, 'بررسی بعدی: ' + report.nextReview, report.limits].join('\n');
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {buildReport, summary};
  if (typeof document === 'undefined') return;

  function init(root) {
    if (root.dataset.tnTriageReady) return;
    const find = selector => root.querySelector(selector);
    const problem = find('[data-tn-triage-problem]'), scope = find('[data-tn-triage-scope]');
    const articles = [...root.querySelectorAll('[data-tn-triage-rule]')], steps = [...root.querySelectorAll('[data-tn-triage-step]')];
    const next = find('[data-tn-triage-next]'), back = find('[data-tn-triage-back]'), build = find('[data-tn-triage-build]');
    const reset = find('[data-tn-triage-reset]'), download = find('[data-tn-triage-download]');
    const result = find('[data-tn-triage-result]'), progress = find('[data-tn-triage-progress]');
    const model = Object.create(null);
    for (const article of articles) {
      const observations = Object.create(null);
      for (const option of article.querySelectorAll('option')) observations[option.value] = {label: option.textContent, advice: option.dataset.advice};
      model[article.dataset.tnTriageRule] = {title: article.querySelector('h4').textContent,
        test: article.querySelector('[data-tn-triage-test]').textContent, why: article.querySelector('[data-tn-triage-why]').textContent,
        source: article.querySelector('a').href, observations};
    }
    if (issueKeys.some(key => !own(model, key))) return; // Retain the complete manual fallback if markup is incomplete.
    let step = 1, report = null;
    function clearResult() { report = null; result.hidden = true; download.disabled = true; find('[data-tn-triage-summary]').value = ''; }
    function show(focus) {
      steps.forEach(field => { field.hidden = Number(field.dataset.tnTriageStep) !== step; });
      articles.forEach(article => { article.hidden = article.dataset.tnTriageRule !== problem.value; });
      next.hidden = step === 3; next.disabled = step === 1 && !own(model, problem.value);
      back.hidden = step === 1; back.disabled = false; build.hidden = step !== 3; build.disabled = false; reset.hidden = false; reset.disabled = false;
      progress.textContent = 'مرحلهٔ ' + step + ' از ۳' + (own(model, problem.value) ? ' · ' + model[problem.value].title : '');
      if (focus) (step === 1 ? problem : step === 2 ? scope : articles.find(a => a.dataset.tnTriageRule === problem.value).querySelector('select')).focus();
    }
    problem.addEventListener('change', () => { articles.forEach(a => { a.querySelector('select').value = 'unknown'; }); clearResult(); show(false); });
    scope.addEventListener('change', clearResult);
    articles.forEach(article => article.querySelector('select').addEventListener('change', clearResult));
    next.addEventListener('click', () => { if (!own(model, problem.value)) return; step = Math.min(step + 1, 3); clearResult(); show(true); });
    back.addEventListener('click', () => { step = Math.max(step - 1, 1); clearResult(); show(true); });
    build.addEventListener('click', () => {
      const article = articles.find(a => a.dataset.tnTriageRule === problem.value); if (!article) return;
      report = buildReport(model, {problem: problem.value, scope: scope.value, observation: article.querySelector('select').value});
      find('[data-tn-triage-advice]').textContent = report.nextReview;
      find('[data-tn-triage-summary]').value = summary(report); result.hidden = false; download.disabled = false;
      find('[data-tn-triage-summary]').focus();
    });
    download.addEventListener('click', () => {
      if (!report) return;
      const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], {type: 'application/json;charset=utf-8'}));
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'tehnet-network-triage.json'; root.appendChild(anchor); anchor.click(); anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    reset.addEventListener('click', () => { problem.value = ''; scope.value = 'unknown'; articles.forEach(a => { a.querySelector('select').value = 'unknown'; }); step = 1; clearResult(); show(true); });
    root.dataset.tnTriageReady = '1'; show(false);
  }
  const start = () => document.querySelectorAll('[data-tn-triage]').forEach(init);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true}); else start();
}());
