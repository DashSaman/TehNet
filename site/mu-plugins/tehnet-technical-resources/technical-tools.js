/* Pure local calculation: no network, cookies, telemetry or router changes. */
document.querySelectorAll('[data-tn-mtu]').forEach(tool=>{
 const path=tool.querySelector('[data-tn-path-mtu]'),ip=tool.querySelector('[data-tn-outer-ip]'),out=tool.querySelector('[data-tn-mtu-result]');
 const calculate=()=>{
  const p=Number(path.value),v=Number(ip.value);path.min=v===6?'1280':'576';
  if(!Number.isInteger(p)||p<Number(path.min)||p>9000){out.textContent=`MTU مسیر باید عدد صحیح بین ${path.min} و 9000 باشد.`;return;}
  const inner=p-(v===6?80:60);out.textContent=`MTU داخلی محاسباتی: ${inner.toLocaleString('fa-IR')} بایت؛ سربار ${v===6?80:60} بایت. ${inner<1280?'برای IPv6 داخلی، حداقل MTU و سازوکار مسیر را جدا بررسی کنید.':'پیش از تغییر روتر، نتیجه را در سناریوی واقعی بررسی کنید.'}`;
  tool.dispatchEvent(new CustomEvent('tn:tool-calculated',{bubbles:true,detail:{tool:'wireguard-mtu',outer_ip:v}}));
 };
 tool.querySelector('[data-tn-mtu-calculate]').addEventListener('click',calculate);
 ip.addEventListener('change',calculate);path.addEventListener('change',calculate);
});
