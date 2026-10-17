/* TehNet presentation preferences and explicit copy buttons; no network requests. */
(function () {
  'use strict';
  const root = document.documentElement;
  const toggle = document.querySelector('.theme-toggle');
  function applyTheme(value) {
    root.dataset.theme = value === 'light' ? 'light' : 'dark';
    const light = root.dataset.theme === 'light';
    toggle.setAttribute('aria-pressed', String(light));
    toggle.setAttribute('aria-label', light ? 'فعال‌کردن حالت تیره' : 'فعال‌کردن حالت روشن');
    toggle.textContent = light ? 'حالت تیره' : 'حالت روشن';
    document.querySelector('meta[name="theme-color"]').content = light ? '#f5f8fb' : '#080f18';
  }
  try { applyTheme(localStorage.getItem('tn-theme')); } catch (error) { applyTheme('dark'); }
  toggle.addEventListener('click', function () {
    applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
    try { localStorage.setItem('tn-theme', root.dataset.theme); } catch (error) {}
  });
  window.addEventListener('storage', function (event) {
    if (event.key === 'tn-theme') applyTheme(event.newValue);
  });
  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', async function () {
      const field = document.getElementById(button.dataset.copy);
      const status = document.getElementById('copy-status');
      try {
        await navigator.clipboard.writeText(field.value);
        status.textContent = 'فرمان کپی شد؛ آن را در ترمینال سیستم اوبونتو خود اجرا کنید.';
      } catch (error) {
        field.focus(); field.select();
        status.textContent = 'فرمان انتخاب شد؛ با Ctrl+C یا گزینه کپی آن را بردارید.';
      }
    });
  });
}());
