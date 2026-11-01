(() => {
  'use strict';
  const enhance = gallery => {
    const update = () => {
      const images = [...gallery.querySelectorAll('.flex-control-thumbs li img')];
      images.forEach((image, index) => {
        let button = image.parentElement;
        if (button?.tagName === 'LI') {
          button = document.createElement('button');
          button.type = 'button';
          button.className = 'tn-gallery-thumb';
          image.before(button);
          button.append(image);
          button.addEventListener('click', event => {
            // FlexSlider owns the original image click. Avoid a second pointer activation.
            if (event.target === button) image.click();
          });
        }
        if (!button?.matches('button.tn-gallery-thumb')) return;
        button.setAttribute('aria-label', `نمایش تصویر ${(index + 1).toLocaleString('fa-IR')} از ${images.length.toLocaleString('fa-IR')}`);
        button.setAttribute('aria-current', String(image.classList.contains('flex-active')));
      });
    };
    // WooCommerce may create its thumbnails after this footer script has run.
    const observer = new MutationObserver(update);
    observer.observe(gallery, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    update();
  };
  const init = () => document.querySelectorAll('.woocommerce-product-gallery').forEach(enhance);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
