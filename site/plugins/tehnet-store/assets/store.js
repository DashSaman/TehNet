(() => {
  'use strict';
  const dialog = document.querySelector('#tn-store-dialog');
  if (!dialog) return;
  const feedback = document.querySelector('#tn-store-feedback');
  const ajax = location.origin + '/wp-admin/admin-ajax.php';
  const validItem = p => p && Number.isSafeInteger(p.id) && typeof p.name === 'string' && typeof p.url === 'string' && new URL(p.url, location.origin).origin === location.origin;
  const syncWishlist = () => {
    if (!document.body.classList.contains('logged-in') || !dialog.dataset.tnNonce) return;
    const body = new URLSearchParams({action:'tn_wishlist_sync', nonce:dialog.dataset.tnNonce, items:JSON.stringify(lists.wishlist)});
    fetch(ajax,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded'},body})
      .then(r=>r.ok?r.json():null).then(merged=>{ if(Array.isArray(merged)){ lists.wishlist=merged.filter(validItem); save('wishlist'); } }).catch(()=>{});
  };
  syncWishlist();
  (() => {
    const input=document.querySelector('.tn-filter-search input[name="s"]');
    if(!input) return;
    let timer=null,box=null,index=-1,lastItems=[];
    const close=()=>{ if(box){box.remove();box=null;index=-1;lastItems=[];} };
    const go=item=>{ close(); location.href=item.url; };
    const render=items=>{
      close();
      if(!items.length) return;
      lastItems=items;
      box=document.createElement('ul');box.className='tn-suggest';box.setAttribute('role','listbox');
      items.forEach(item=>{
        const li=document.createElement('li');li.setAttribute('role','option');
        li.append(document.createTextNode(item.name));
        if(item.sku){const sku=document.createElement('small');sku.dir='ltr';sku.textContent=' '+item.sku;li.append(sku);}
        li.addEventListener('mousedown',e=>{e.preventDefault();go(item);});
        box.append(li);
      });
      input.parentElement.append(box);index=-1;
    };
    const highlight=()=>{ if(!box)return; [...box.children].forEach((li,i)=>li.classList.toggle('tn-suggest-active',i===index)); };
    input.addEventListener('input',()=>{
      clearTimeout(timer);const q=input.value.trim();
      if(q.length<2){close();return;}
      timer=setTimeout(async()=>{ try{ const r=await fetch(ajax+'?action=tn_suggest&term='+encodeURIComponent(q),{credentials:'same-origin'}); render(r.ok?await r.json():[]); }catch{close();} },250);
    });
    input.addEventListener('keydown',e=>{
      if(!box||!lastItems.length){return;}
      if(e.key==='ArrowDown'){e.preventDefault();index=(index+1)%lastItems.length;highlight();}
      else if(e.key==='ArrowUp'){e.preventDefault();index=(index-1+lastItems.length)%lastItems.length;highlight();}
      else if(e.key==='Enter'&&index>=0&&lastItems[index]){e.preventDefault();go(lastItems[index]);}
      else if(e.key==='Escape'){close();}
    });
    document.addEventListener('click',e=>{ if(box&&!input.parentElement.contains(e.target))close(); });
  })();
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
    syncButtons();
  }
  function syncButtons() {
    document.querySelectorAll('[data-tn-add]').forEach(button=>{
      try{const kind=button.dataset.tnAdd,item=JSON.parse(button.closest('[data-tn-product]').dataset.tnProduct);
      const active=lists[kind]?.some(p=>p.id===item.id);button.setAttribute('aria-pressed',String(Boolean(active)));
      button.textContent=kind==='compare'?(active?'حذف از مقایسه':'مقایسه'):(active?'حذف از علاقه‌مندی':'علاقه‌مندی');}catch{}
    });
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
      const sku = document.createElement('p'); sku.textContent = item.sku || 'شناسه تأیید نشده';sku.dir='ltr';
      const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'حذف';
      remove.addEventListener('click', () => { lists[kind] = lists[kind].filter(p => p.id !== item.id); save(kind); show(kind); });
      card.append(link, sku, details, remove); container.append(card);
    }
    if (kind === 'compare' && lists[kind].length) {
      const wrap=document.createElement('div');wrap.className='tn-comparison-table';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','جدول مقایسه مشخصات تأییدشده');
      const table=document.createElement('table'),caption=document.createElement('caption');caption.textContent='مشخصات تأییدشده؛ مورد نامعلوم با حدس تکمیل نمی‌شود.';table.append(caption);
      const head=document.createElement('tr'),corner=document.createElement('th');corner.textContent='مشخصه';corner.scope='col';head.append(corner);
      for(const item of lists[kind]){const cell=document.createElement('th');cell.scope='col';cell.textContent=item.name;head.append(cell);}const thead=document.createElement('thead');thead.append(head);table.append(thead);
      const body=document.createElement('tbody');
      const fa=n=>Number(n).toLocaleString('fa-IR');
      for(const [label,value] of [['قیمت',p=>p.price_irr>0?fa(p.price_irr)+' ریال':'نیازمند استعلام'],['واحد فروش',p=>p.unit],['حداقل مقدار',p=>p.minimum],['شیلد',p=>p.specs?.shield],['روکش',p=>p.specs?.jacket],['محیط نصب',p=>p.specs?.environment]]){
        const row=document.createElement('tr'),name=document.createElement('th');name.scope='row';name.textContent=label;row.append(name);
        for(const item of lists[kind]){const cell=document.createElement('td');cell.textContent=value(item)||'تأیید نشده';row.append(cell);}body.append(row);
      }
      table.append(body);wrap.append(table);container.append(wrap);
      const declaredKeys=[];for(const item of lists[kind]){for(const key of Object.keys(item.source_specs||{})){if(!declaredKeys.includes(key))declaredKeys.push(key);}}
      if(declaredKeys.length){
        const dwrap=document.createElement('div');dwrap.className='tn-comparison-table';dwrap.tabIndex=0;dwrap.setAttribute('role','region');dwrap.setAttribute('aria-label','جدول مشخصات اعلام‌شدهٔ منبع');
        const dtable=document.createElement('table'),dcaption=document.createElement('caption');dcaption.textContent='اعلام فروشندهٔ منبع؛ توسط تهران نتورک تأیید نشده و مبنای انتخاب نهایی نیست.';dtable.append(dcaption);
        const dhead=document.createElement('tr'),dcorner=document.createElement('th');dcorner.textContent='مشخصه (اعلام منبع)';dcorner.scope='col';dhead.append(dcorner);
        for(const item of lists[kind]){const cell=document.createElement('th');cell.scope='col';cell.textContent=item.name;dhead.append(cell);}
        const dthead=document.createElement('thead');dthead.append(dhead);dtable.append(dthead);
        const dbody=document.createElement('tbody');
        for(const key of declaredKeys.slice(0,10)){
          const row=document.createElement('tr'),name=document.createElement('th');name.scope='row';name.textContent=key;row.append(name);
          for(const item of lists[kind]){const cell=document.createElement('td');cell.textContent=item.source_specs?.[key]||'—';row.append(cell);}dbody.append(row);
        }
        dtable.append(dbody);dwrap.append(dtable);container.append(dwrap);
      }
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
        if (existing) lists[kind]=lists[kind].filter(p=>p.id!==item.id); else lists[kind].push(item);
        save(kind); feedback.textContent = existing?'کالا از انتخاب‌های شما حذف شد.':'کالا به انتخاب‌های شما اضافه شد.';
      if (kind==='wishlist') syncWishlist();
      } catch { feedback.textContent = 'اطلاعات کالا قابل خواندن نیست.'; }
    }
    const open = event.target.closest('[data-tn-open]');
    if (open && open.dataset.tnOpen in lists) show(open.dataset.tnOpen);
    if (event.target.closest('[data-tn-close]')) dialog.close();
  });
  for (const kind of Object.keys(lists)) save(kind);
})();
