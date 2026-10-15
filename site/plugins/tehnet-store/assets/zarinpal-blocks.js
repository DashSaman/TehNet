/* Woo owns checkout validation and process_payment. No card data is collected. */
(() => {
    'use strict';
    const settings = window.wc.wcSettings.getSetting('tn_zarinpal_sandbox_data', {});
    const label = settings.title || 'پرداخت آزمایشی زرین‌پال (بدون انتقال وجه)';
    const content = window.wp.element.createElement('p', null, settings.description || 'فقط کالای ساختگی؛ وجه واقعی جابه‌جا نمی‌شود.');
    window.wc.wcBlocksRegistry.registerPaymentMethod({
        name: 'tn_zarinpal_sandbox', paymentMethodId: 'tn_zarinpal_sandbox',
        label: window.wp.element.createElement('span', null, label), ariaLabel: label,
        content, edit: content, canMakePayment: () => true,
        supports: { features: ['products'], showSavedCards: false, showSaveOption: false }
    });
})();
