/* TehNet website presentation: theme, navigation, skill filters, print. */
(function () {
  'use strict';
  const root = document.documentElement;
  root.classList.add('tn-js');
  const theme = document.querySelector('.tn-theme-toggle');
  function syncTheme() {
    const light = root.dataset.theme === 'light';
    if (theme) {
      theme.setAttribute('aria-pressed', String(light));
      theme.setAttribute('aria-label', light ? 'فعال‌کردن حالت تیره' : 'فعال‌کردن حالت روشن');
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = light ? '#f5f8fb' : '#080f18';
  }
  if (theme) theme.addEventListener('click', function () {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('tn-theme', root.dataset.theme); } catch (error) {}
    syncTheme();
  });
  syncTheme();
  const toggle = document.querySelector('.tn-menu-toggle');
  const nav = document.getElementById('tn-main-menu');
  const submenus = [];
  function closeSubmenus(except) {
    submenus.forEach(function (entry) {
      if (entry !== except) { entry.item.classList.remove('is-submenu-open'); entry.button.setAttribute('aria-expanded', 'false'); }
    });
  }
  if (nav) nav.querySelectorAll('li.menu-item-has-children').forEach(function (item, index) {
    const list = item.querySelector(':scope > ul.sub-menu');
    const link = item.querySelector(':scope > a');
    if (!list || !link) return;
    list.id = 'tn-submenu-' + index;
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'tn-submenu-toggle';
    button.setAttribute('aria-label', 'زیرمنوی ' + link.textContent.trim());
    button.setAttribute('aria-expanded', 'false'); button.setAttribute('aria-controls', list.id);
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
    item.insertBefore(button, list);
    const entry = { item: item, button: button };
    submenus.push(entry);
    button.addEventListener('click', function () {
      const open = button.getAttribute('aria-expanded') !== 'true'; closeSubmenus(entry);
      item.classList.toggle('is-submenu-open', open); button.setAttribute('aria-expanded', String(open));
    });
  });
  function setMenu(open, restoreFocus) {
    if (!toggle || !nav) return;
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'بستن منو' : 'بازکردن منو');
    if (!open) closeSubmenus();
    if (restoreFocus) toggle.focus();
  }
  if (toggle && nav) {
    toggle.addEventListener('click', function () { setMenu(toggle.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (event) { if (event.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (event) {
      const expanded = submenus.find(function (entry) { return entry.button.getAttribute('aria-expanded') === 'true'; });
      if (event.key === 'Escape' && expanded) { closeSubmenus(); expanded.button.focus(); event.preventDefault(); return; }
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') setMenu(false, true);
    });
    document.addEventListener('click', function (event) {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) { setMenu(false); closeSubmenus(); }
    });
    window.addEventListener('resize', function () { if (innerWidth > 1050) setMenu(false); });
  }
  const motion = document.getElementById('tn-motion-toggle');
  if (motion) motion.addEventListener('click', function () {
    const paused = root.classList.toggle('tn-motion-paused');
    motion.setAttribute('aria-pressed', String(paused));
    motion.textContent = paused ? 'پخش حرکت‌های گرافیکی' : 'توقف حرکت‌های گرافیکی';
  });
  const filters = Array.from(document.querySelectorAll('[data-tn-filter]'));
  const skills = Array.from(document.querySelectorAll('.tn-skill'));
  filters.forEach(function (button) {
    button.addEventListener('click', function () {
      filters.forEach(function (other) { other.setAttribute('aria-pressed', String(other === button)); });
      skills.forEach(function (skill) { skill.hidden = button.dataset.tnFilter !== 'all' && skill.dataset.group !== button.dataset.tnFilter; });
    });
  });
  let printStates = [];
  window.addEventListener('beforeprint', function () {
    printStates = Array.from(document.querySelectorAll('.tn-work')).map(function (element) { return [element, element.open]; });
    printStates.forEach(function (state) { state[0].open = true; });
  });
  window.addEventListener('afterprint', function () {
    printStates.forEach(function (state) { state[0].open = state[1]; });
    printStates = [];
  });
  document.querySelectorAll('[data-tn-print]').forEach(function (button) {
    button.addEventListener('click', function () { window.print(); });
  });
}());
