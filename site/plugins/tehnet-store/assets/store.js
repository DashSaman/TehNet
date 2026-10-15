(() => {
  'use strict';
  const dialog = document.querySelector('#tn-store-dialog');
  if (!dialog) return;
  const feedback = document.querySelector('#tn-store-feedback');
  const lists = { compare: [], wishlist: [] };
  for (const kind of Object.keys(lists)) {
    try {
      const saved = JSON.parse(localStorage.getItem(`tn-store-v1-${kind}`) || '[]');
      if (Array.isArray(saved)) lists[kind] = saved.filter(p => Number.isSafeInteger(p.id) && typeof p.name === 'string' && typeof p.url === 'string' && new URL(p.url, location.origin).origin === location.origin).slice(0, kind === 'compare' ? 4 : 24);
    } catch { /* Storage can be unavailable; in-memory tools still work. */ }
  }
  function save(kind) {
    try { localStorage.setItem(`tn-store-v1-${kind}`, JSON.stringify(lists[kind])); } catch { feedback.textContent = 'ذخیره روی این مرورگر ممکن نیست؛ انتخاب‌ها فقط در همین صفحه می‌مانند.'; }
    document.querySelectorAll(`[data-tn-count="${kind}"]`).forEach(el => { el.textContent = lists[kind].length.toLocaleString('fa-IR'); });
  }
  function show(kind) {
    const container = document.querySelector('#tn-store-dialog-content');
    container.replaceChildren();
    document.querySelector('#tn-store-dialog-title').textContent = kind === 'compare' ? 'مقایسه کالاها' : 'علاقه‌مندی‌های شما';
    if (!lists[kind].length) { const p = document.createElement('p'); p.textContent = 'هنوز کالایی انتخاب نشده است.'; container.append(p); }
    for (const item of lists[kind]) {
      const card = document.createElement('article');
      const link = document.createElement('a'); link.href = item.url; link.textContent = item.name;
      const details = document.createElement('p'); details.textContent = `${item.price || 'نیازمند استعلام'} · واحد: ${item.unit || 'تأیید نشده'}`;
      const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'حذف';
      remove.addEventListener('click', () => { lists[kind] = lists[kind].filter(p => p.id !== item.id); save(kind); show(kind); });
      card.append(link, details, remove); container.append(card);
    }
    if (!dialog.open) dialog.showModal();
  }
  document.addEventListener('click', event => {
    const add = event.target.closest('[data-tn-add]');
    if (add) {
      const kind = add.dataset.tnAdd;
      if (!(kind in lists)) return;
      try {
        const item = JSON.parse(add.closest('[data-tn-product]').dataset.tnProduct);
        if (!Number.isSafeInteger(item.id) || new URL(item.url, location.origin).origin !== location.origin) return;
        const existing = lists[kind].find(p => p.id === item.id);
        if (!existing && lists[kind].length >= (kind === 'compare' ? 4 : 24)) { feedback.textContent = 'تعداد انتخاب‌ها به سقف مجاز رسیده است.'; return; }
        if (existing) Object.assign(existing, item); else lists[kind].push(item);
        save(kind); feedback.textContent = 'کالا به انتخاب‌های شما اضافه شد.';
      } catch { feedback.textContent = 'اطلاعات کالا قابل خواندن نیست.'; }
    }
    const open = event.target.closest('[data-tn-open]');
    if (open && open.dataset.tnOpen in lists) show(open.dataset.tnOpen);
    if (event.target.closest('[data-tn-close]')) dialog.close();
  });
  for (const kind of Object.keys(lists)) save(kind);
})();
