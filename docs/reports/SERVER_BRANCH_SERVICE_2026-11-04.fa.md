# عمق خدمت سرور و ارتباط شعب —۴نوامبر۲۰۲۶

وضعیت فعلی: **DEPLOYED_VERIFIED**؛ [PR78](https://github.com/DashSaman/TehNet/pull/78) ادغام و CI41849968305 موفق شد. فقط بدنهٔ ID33 از main `7062a514948b0e6701f84782f20f9b5066db88e6`، با payload برابر source qualifyشده منتشر شد. منبع qualifyشده `756fec7d4f19ee04b25085ab94dcd544e1ec69c6`؛ Issue63 باز است و parity اعلام نمی‌شود.

دو ماژول کاربردی به همان [صفحهٔ راه‌اندازی شبکه](https://tehnet.ir/services/network-setup-tehran/) اضافه شده‌اند: ورودی امن بررسی، وابستگی‌ها، عوامل برآورد، خروجی پیشنهادی، معیار پذیرش، محدودیت و مثال فرضی. متن‌های قبلی، ازجمله Wi-Fi، حفظ شده‌اند؛ یادداشت ویراستاری به انتهای کل مطلب منتقل و دو پیوند دسترسی سریع اضافه شده‌اند. صفحه، فرم، backend یا URL تازه ساخته نشده است.

- `#server-project-brief`: سرور/مجازی‌سازی، بار کاری و مجوز، نقش RPO/RTO در توافق، مهاجرت و بررسی بازیابی. CTA به `/services/?tn_service_context=server-scoping#service-request`.
- `#branch-connectivity-brief`: ارتباط شعب، سرویس‌های مجاز، هم‌پوشانی آدرس، وابستگی مسیر/نام/برنامه، آزمون قطعی و مستندات. CTA به `/services/?tn_service_context=wifi-branch-scoping#service-request`.

پشتیبانی فنی دو نکته با بازبینی۴نوامبر: [Microsoft؛ تفاوت checkpointها](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/checkpoints) و [MikroTik؛ allowed-address در peerهای یک interface](https://manual.mikrotik.com/docs/cli-reference/interface/wireguard/peers/). این‌ها گواهی مهارت، تضمین سازگاری یا نتیجهٔ اجرای پروژه نیستند. مسئولیت PBX/IVR همچنان با ارجاع مرتبط به MyTel مستقل تفکیک شده است.

## شواهد واقعی

[receipt عمومی staging](../evidence/2026-11-04/server-branch/native-staging.json). پیش از ویرایش، بدنهٔ ID33 با منبع عمومی مخزن به هش `6042d2d…` منطبق بود. فقط `post_content` این هویت در scope جدید مجاز است؛ title/excerpt/slug/parent/status/meta حفظ می‌شوند و0فایل runtime مالکیت انتشار دارد.

| بررسی | نتیجه |
|---|---|
| unit مرز release | RED برای scope غایب؛ سپس29آزمون،28PASS/1SKIP مربوط به symlink Windows |
| syntax | PHP lint دو فایل و Node check موفق |
| native |39بررسی؛ preflight/apply/repeat/rollback، داده و revision، رد drift/side effect و row lock نویسندهٔ دوم |
| مرورگر |106بررسی؛1440/375 دو تم و320بدون JS، یک H1، canonical/noindex/RTL، منابع و پیوندهای سریع |
| مسیر درخواست | هر دو لینک واقعی ماژول به فرم موجود می‌روند؛ context انتخاب‌شده، nonce واقعی و `tn_ticket_submit` در همهٔ حالت‌ها بررسی شدند |
| cleanup | تمام posts/meta/users/revisions، فایل‌های guard و runtimeهای قبلی دقیقاً بازیابی شدند |
| ارسال |0تیکت در این اجرای خواندنی و0تغییر production |

fixture صفحهٔ Services فقط برای آزمون فرم موجود به منبع فعلی تطبیق و پس از پایان دقیقاً بازیابی شد؛ جزو دامنهٔ انتشار این بسته نیست. آزمون اول مرورگر در انتظار تکمیل ناوبری کلیک متوقف شد و **FAILED_RESTORED** باقی ماند؛ آزمون اصلاح‌شده با رسیدن به صفحهٔ فرم و بررسی خودِ کنترل‌های آن، بدون force click یا حذف assertionها، موفق شد. این بسته ادعای ارسال تیکت تازه ندارد؛ پذیرش قدیمیِ دو تیکت synthetic زیرساخت canonical در PR64/65، شاهد جداگانه و تاریخی است.

## مشاهدهٔ قبل / بعد

قبل، بالای همان صفحهٔ عمومی بود؛ دو ماژول تازه در بدنهٔ با هش6042d2d وجود نداشتند. بعد، بخش‌های تازه در staging هستند؛ این تصاویر مقایسهٔ یک viewport یکسان یا بازطراحی کل قالب را ادعا نمی‌کنند.

- [قبل؛ موبایل روشن](../evidence/2026-11-04/server-branch/before-existing-service-375-light.png).
- [بعد؛ ماژول سرور، موبایل روشن](../evidence/2026-11-04/server-branch/after-server-project-brief-375-light.png).
- [بعد؛ ارتباط شعب، موبایل تیره](../evidence/2026-11-04/server-branch/after-branch-connectivity-brief-375-dark.png).

انتشار واقعی با backup تازه/checksum، drift guard و rollback واجد آزمون انجام شد. [رسید production](../evidence/2026-11-04/server-branch/production-verification.json)،106بررسی مرورگر زنده و0ارسال فرم؛ noindex،25قلم، داده/فایل‌های دیگر، runtime، theme/menu/cron/CAPTCHA و پرداخت دقیقاً حفظ شدند. [سرور در موبایل روشن](../evidence/2026-11-04/server-branch/live-server-project-brief-375-light.png) و [شعب در موبایل تیره](../evidence/2026-11-04/server-branch/live-branch-connectivity-brief-375-dark.png). گام بعد: پیوند مستقیم دو کارت کاتالوگ به جزئیات همین مالک، سپس تصمیم‌یار دستی و لاب آموزشی؛ انتشار این بسته دوباره اجرا نشود. noindex، پرداخت، MyTel و گیت‌های credential/history/origin/shared-network حفظ می‌شوند. هیچ Hyper-V، تونل، backup/restore مشتری، کارایی شبکه، SLA، رتبه/traffic/AI citation یا conversion در این بسته اندازه‌گیری نشده است.
