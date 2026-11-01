/* Explicit v2 rendering supports every existing intake on the same page. */
(() => {
    'use strict';
    const nodes = [...document.querySelectorAll('[data-tn-recaptcha]')];
    if (!nodes.length) return;
    const status = (node, text) => { node.closest('.tn-captcha').querySelector('.tn-captcha-status').textContent = text; };
    window.tnRecaptchaReady = () => {
        nodes.forEach(node => {
            if (node.dataset.rendered) return;
            node.dataset.rendered = 'true';
            window.grecaptcha.render(node, {
                sitekey: node.dataset.tnRecaptcha,
                size: node.clientWidth < 304 ? 'compact' : 'normal',
                callback: () => status(node, 'بررسی انجام شد؛ می‌توانید درخواست را ثبت کنید.'),
                'expired-callback': () => status(node, 'اعتبار بررسی پایان یافت؛ دوباره آن را تکمیل کنید.'),
                'error-callback': () => status(node, 'ارتباط با Google برقرار نشد. دوباره تلاش کنید یا از راه‌های تماس استفاده کنید.')
            });
        });
    };
    const script = document.createElement('script');
    script.src = 'https://www.google.com/recaptcha/api.js?onload=tnRecaptchaReady&render=explicit&hl=fa';
    script.async = true;
    script.defer = true;
    script.onerror = () => nodes.forEach(node => status(node, 'سرویس Google بارگیری نشد. دوباره تلاش کنید یا با ما تماس بگیرید.'));
    document.head.append(script);
})();
