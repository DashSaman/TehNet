(() => {
  'use strict';
  document.querySelectorAll('[data-tn-model]').forEach(root => {
    const button = root.querySelector('[data-tn-model-load]');
    button.addEventListener('click', async () => {
      button.disabled = true;
      try {
        const module = await import(root.dataset.module);
        module.mount(root);
        root.querySelector('.tn-model-stage').hidden = false;
        button.hidden = true;
        root.querySelector('canvas').focus();
      } catch {
        button.disabled = false;
        button.textContent = 'بارگذاری انجام نشد؛ دوباره تلاش کنید';
      }
    }, { once: false });
  });
})();
