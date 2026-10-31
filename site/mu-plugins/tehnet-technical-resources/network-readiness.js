(function () {
  'use strict';
  const allowed = ['unknown', 'ready', 'issue', 'na'];
  function summarize(values) {
    if (!Array.isArray(values)) throw new TypeError('A list of manual states is required');
    const result = { unknown: 0, ready: 0, issue: 0, na: 0 };
    for (const value of values) result[allowed.includes(value) ? value : 'unknown']++;
    return result;
  }
  if (typeof module === 'object' && module.exports) module.exports = { summarize };
  if (typeof document === 'undefined') return;
  const labels = { unknown: 'هنوز بررسی نشده', ready: 'مدرک بررسی موجود است', issue: 'نیاز به اصلاح دارد', na: 'کاربرد ندارد' };
  document.querySelectorAll('[data-tn-readiness]').forEach(root => {
    const fields = [...root.querySelectorAll('[data-tn-readiness-select]')];
    const summary = root.querySelector('[data-tn-readiness-summary]');
    const report = root.querySelector('[data-tn-readiness-report]');
    const exportButton = root.querySelector('[data-tn-readiness-export]');
    const resetButton = root.querySelector('[data-tn-readiness-reset]');
    const number = new Intl.NumberFormat('fa-IR');
    function update() {
      const counts = summarize(fields.map(field => field.value));
      summary.textContent = `نیاز به اصلاح: ${number.format(counts.issue)} · بررسی‌نشده: ${number.format(counts.unknown)} · دارای مدرک: ${number.format(counts.ready)} · بدون کاربرد: ${number.format(counts.na)}`;
      report.hidden = true;
      report.textContent = '';
    }
    fields.forEach(field => field.addEventListener('change', update));
    resetButton.addEventListener('click', () => {
      fields.forEach(field => { field.value = 'unknown'; });
      update();
      fields[0]?.focus();
    });
    exportButton.addEventListener('click', () => {
      const data = {
        schema: 'tehnet.voice-network-checklist.v1',
        type: 'manual-self-assessment', measured: false,
        recorded_at: new Date().toISOString(),
        answers: fields.map(field => {
          const group = field.closest('[data-tn-readiness-item]');
          return { key: group.dataset.key, question: group.querySelector('legend').textContent, state: field.value };
        })
      };
      report.textContent = 'گزارش دستی؛ بدون اندازه‌گیری یا تأیید فنی شبکه\n' + data.answers.map(answer => `${answer.question}: ${labels[answer.state]}`).join('\n');
      report.hidden = false;
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' }));
      const link = document.createElement('a');
      link.href = url; link.download = 'tehnet-voice-network-checklist.json';
      document.body.appendChild(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    exportButton.disabled = resetButton.disabled = false;
    update();
  });
})();
