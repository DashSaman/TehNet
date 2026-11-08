# گزارش آماده‌سازی MTCNA — ۸ نوامبر ۲۰۲۶ (فقط پیش‌نویس)

**محدوده:** ایجاد یک پیش‌نویس خصوصی WordPress و ثبت مستندات در شاخهٔ مستقل `content/mtcna-prep-20261108-scoped-280`، بدون تغییر PR82.

## خط مبنای واقعی
- WPVibe Free در ابتدا ۰ از ۱۰۰ فراخوانی مصرف داشت؛ هیچ Usage Reset مصرف نشد.
- قبل از ایجاد ۳۴ Draft در WordPress با parent=40 و status=draft ثبت شد؛ پس از ایجاد ۳۵ Draft با همین فیلتر بازخوانی شد.
- شمار pageهای parent=40 با status=future در REST صفر (`[]`) است؛ هیچ وضعیت published/future دستکاری نشده است.
- شش جلسهٔ تنها-GitHub: ۱۵، ۲۶، ۲۸، ۳۰، ۳۲ و ۴۰؛ legacy ID255 حفظ شد.

## تغییر WordPress
- جلسهٔ ۲۳، «سخت‌سازی Firewall، حفظ مدیریت و بازگشت امن در RouterOS 7»، با ID280، parent=40، status=draft و slug یکتا در ساعت ۱۶:۲۰:۱۵ تهران ایجاد شد.
- [آدرس مستقیم WordPress](https://tehnet.ir/?page_id=280) و [ویرایش](https://tehnet.ir/wp-admin/post.php?post=280&action=edit) و [پیش‌نمایش متکی به لاگین](https://tehnet.ir/?page_id=280&preview=true). بازشدن مرورگری ویرایش/پیش‌نمایش مستقلاً آزموده نشده است.
- پاسخ ایجاد حاوی متن Gutenberg بود و GET مستقل برای ID/status/parent/title/slug/excerpt موفق شد.
- **عدم‌تأیید:** هر GET مستقل برای content.raw صفحه ۲۸۰ (حتی با _fields) نتیجهٔ خالی `{}` داد. در نتیجه تطابق تمام متن/هش و Gutenberg editor-save هنوز NOT_VERIFIED است؛ این پاسخ خالی اثبات‌کنندهٔ خالی‌بودن محتوا نیست.
- متن شامل H2، نمونه فرمان/انتظار، rollback کم‌خطر، تصویر شماتیک با alt، منابع رسمی، لینک داخلی، excerpt و پیشنهاد meta description داخل کامنت HTML است؛ پیشنهاد meta به معنی تنظیم SEO plugin metadata نیست.
- دو تصویر WinBox با URL خارجی GitHub در محتوای ارسالی قرار گرفتند، نه در Media Library؛ هیچ آپلود WordPress انجام نشد.

## اسکرین‌شات‌های اصیل و مرز شواهد
۱. [نمای خالی Firewall Filter Rules، ۲۰۲۶-۱۱-۰۴](https://github.com/DashSaman/TehNet/blob/content/mtcna-saturday-20261107/content/mtcna/screenshots/real-lab/2026-11-04/winbox40/lesson-23/02-panel.png).
۲. [New Rule ذخیره‌نشده با Chain=forward، ۲۰۲۶-۱۱-۰۴](https://github.com/DashSaman/TehNet/blob/content/mtcna-saturday-20261107/content/mtcna/screenshots/real-lab/2026-11-04/winbox40/lesson-23/03-form-or-readonly.png).

هر دو از WinBox Linux 4.5 روی CHR RouterOS 7.25.1 واقعی‌اند و جداگانه بازرسی بصری شدند؛ هیچ‌یک فرم پرشده، Apply/OK، Counter موفق یا rollback را اثبات نمی‌کند. تصویر اول جدول خالی است؛ تصویر دوم فرم پیش‌فرض forward دارد، نه قانون input ذخیره‌شده.

## توقف و کار بعدی
- توقف پس از یک درس به‌دلیل فقدان readback خام مطمئن؛ درس دوم ساخته نشد.
- ابتدا content.raw صفحه ۲۸۰ را با REST معتبر دریافت و drift/hash و Gutenberg editor-save را تأیید کنید؛ در صورت نیاز اصلاح فقط scoped باشد.
- درس‌ها تا کسب آزمون لاب ایزوله، تصویر اصیل چهار مرحله، rollback، بررسی تخصصی و گیت انتشار نه READY هستند و نه SCHEDULED.
- noindex، MyTel، فروشگاه، پرداخت، کاربرها، فرم‌ها، تم، cron، RoboT، شبکه، Docker، رمزها و PR82 دست‌نخورده‌اند. PR82 در خوانش این نوبت open/mergeable=false بود.
- اتوماسیون آماده‌سازی فعال بماند؛ اتوماسیون انتشار مستقل است.
