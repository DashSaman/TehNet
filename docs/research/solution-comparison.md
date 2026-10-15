# مقایسه راهکارها و تصمیم — ۱۵ اکتبر ۲۰۲۶

تصمیم: حفظ storefront موجود WooCommerce و استفاده از ERPNext برای دفتر کل و گردش انبار. اتصال قدیمی WooCommerce داخلی ERPNext از نسخه ۱۵ deprecated است؛ نباید مبنای اتصال جدید شود. اجرای ERP ابتدا فقط در محیط آزمایش محلی انجام می‌شود.

| گزینه | مجوز و نگهداری مشاهده‌شده | امکانات نسخه متن‌باز | فارسی/RTL و ایران | منابع/هزینه اتصال در این پروژه |
|---|---|---|---|---|
| [WooCommerce](https://github.com/woocommerce/woocommerce) | GPL-2.0-or-later؛ مستندات و مخزن فعال | سفارش، محصول، تخفیف، موجودی پایه، بازپرداخت؛ دفتر کل دوطرفه کامل نیست | fa_IR و قالب RTL موجود؛ درگاه/حمل ایران نیازمند ارائه‌دهنده واقعی | کمترین تغییر storefront؛ هم‌اکنون در سرویس موجود |
| [ERPNext](https://github.com/frappe/erpnext) | GPL-3.0؛ تصویر رسمی مشاهده‌شده v16.51.0 | حسابداری، خرید/فروش، GL، انبار، UOM، شماره سریال و رزرو | ترجمه/RTL باید روی نسخه اجراشده آزموده شود؛ انطباق مالیاتی ایران احراز نشده | DB/Redis/workers/backend مستقل؛ میزبانی و نگهداری مجزا؛ اتصال متوسط تا زیاد |
| [Odoo Community](https://github.com/odoo/odoo) | LGPL-3.0؛ مخزن و مستندات فعال | stock/sale/purchase/account در کد Community؛ تمام قابلیت‌های Enterprise رایگان فرض نمی‌شوند | فارسی و تقویم و اتصال مالیاتی نیاز بررسی افزونه/مجوز مستقل | PostgreSQL و runtime مستقل؛ اتصال زیاد؛ جابه‌جایی storefront لازم نیست |
| [Medusa](https://github.com/medusajs/medusa) | MIT؛ مخزن فعال | commerce و موجودی/سفارش؛ دفتر کل قانونی کامل احراز نشد | رابط فارسی و اتصال ایران باید ساخته/آزموده شود | Node/PostgreSQL و storefront جدید؛ بازنویسی پرهزینه در سایت WordPress موجود |
| [Saleor](https://github.com/saleor/saleor) | BSD-3-Clause؛ مخزن فعال | GraphQL commerce و سفارش/انبار؛ GL کامل احراز نشد | frontend RTL و درگاه ایران نیاز integration | Python/PostgreSQL/worker و frontend مستقل؛ پیچیدگی بیشتر از حفظ Woo |

مقادیر RAM بالا ادعای حداقل رسمی نیستند؛ برای این میزبان مشترک ۴GB، ظرفیت ERP تولیدی تأیید نشده است. هزینه لایسنس هسته ERPNext صفر است؛ هزینه میزبانی، پشتیبان، ارتقا، اتصال و خدمات ایران صفر فرض نمی‌شود. هیچ افزونه پولی خریداری نشد.

منابع قابلیت: [Woo orders](https://woocommerce.com/document/managing-orders/)، [Woo HPOS](https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/)، [ERPNext integration](https://docs.frappe.io/erpnext/e-commerce-integrations-for-erpnext)، [اتصال deprecated](https://docs.frappe.io/erpnext/woocommerce_integration)، [UOM](https://docs.frappe.io/erpnext/Selling-in-different-UOM)، [رزرو](https://docs.frappe.io/erpnext/stock-reservation)، [گردش Odoo](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/operations_valuation.html).
مجوزها از LICENSE/metadata همان مخازن بررسی شدند؛ فعال‌بودن توسعه به معنای تضمین SLA یا سازگاری اتصال نیست.
