# انتشار محدود خدمات و ابزار شبکه

وضعیت: `VERIFIED` روی clone مستقل؛ انتشار production هنوز انجام نشده است. چهار boundary test و تمرین کامل file+content با source593b30e پاس شدند. رسید: `qa/growth-2026-10-31/release-rehearsal.json`.

`ops/release-growth-content.py` بسته را از blobهای دو commit کامل می‌سازد: source برای شش فایل و manifest/migration، baseline برای checksum نسخهٔ قبلی. فایل operator نیز از همان source می‌آید. CRLF محیط checkout وارد بسته نمی‌شود. config، bundle اجرایی، log، SQL، نسخهٔ قبلی فایل‌ها و journal فقط در محل خصوصی بیرون Git/webroot می‌مانند. config شامل شناسهٔ دقیق app/DB و حساب CLI موجود است؛ نمونه‌ای حاوی مقدار واقعی در مخزن قرار نمی‌گیرد.

روی میزبان، check/apply/rollback سریالی و تحت flock اجرا می‌شوند. staging باید فقط یک شبکهٔ internal و هیچ port منتشرشده داشته باشد. production فقط جفت container و پورت loopback قبلاً مجاز را می‌پذیرد؛ nonce/index/commerce و مسیر محتوا را migration بومی بررسی می‌کند. marker داخلیِ scope مجوز مالک ایجاد نمی‌کند؛ CI و ادغام عادی، backup/checksum تازه و qualification بازیابی مستقل همچنان لازم‌اند.

ترتیب اعمال: سه module، دو کلاس فرم و در آخر MU loader. هر فایل با temp/fsync/rename و checksum کنترل می‌شود؛ directory تازه برای وب قابل پیمایش است. ترتیب بازگشت: اول migration محتوا، سپس loader و کلاس‌ها، در آخر moduleها. مسیر/نوع فایل و تغییر متعلق به دیگری باعث توقف می‌شود. backupهای فایل پیش از undo کنترل می‌شوند. قفل operator هماهنگی ابزارها را فراهم می‌کند؛ ویرایشگر فایل خارج از این قرارداد باید از تغییر هم‌زمان خودداری کند و این ابزار جای filesystem transaction سراسری را نمی‌گیرد.

خطای مبهم commit محتوا، drift یا journal ناقص، `NEEDS_RECONCILIATION` است؛ فایل‌های لازم برای محتوا نگه داشته می‌شوند. پاک‌کردن journal یا retry کور روش رفع مشکل نیست. فقط APPLIED اثبات‌شده اجازهٔ rollback محتوا می‌دهد؛ نبود journal یا FAILED با check مستقلِ baseline و protected digest باید ثابت شود. تغییر مجاز و هم‌زمان دادهٔ دیگران ممکن است این گیت محافظه‌کارانه را متوقف کند؛ آن داده بازنویسی نمی‌شود.

پذیرش clone مستقل از backup: check → apply → repeat → HTTP smoke → rollback → repeat، checksum شش فایل، دادهٔ محافظت‌شده و عدم تغییر runtimeهای موجود پاس شدند. هشت مسیر شامل خانه، shop، دو hub، دو صفحهٔ تازه، تیکت با context و B2B همگی200 و یک H1/noindex داشتند؛ دو canonical درست، ابزار یک نمونه و nonceها داخل فرم خود بودند. دو container و network موقت حذف شدند؛ backupها خصوصی ماندند. clone قبلیِ editor و DB tmpfs آن دست‌نخورده‌اند. آزمون۳۷تایی migration با نبود تغییر PHP دوباره اجرا نشد.

شکست نخست HTTP واقعی بود: directoryهای بازیابی‌شده‌ای که mode محدود داشتند با مالک root استخراج شده بودند، درحالی‌که فایل‌ها به کاربر وب تعلق داشتند. root CLI به آن‌ها دسترسی داشت و native boot پیشین این اختلاف را آشکار نمی‌کرد. شناسایی با مقایسهٔ shortcode registry در HTTP و CLI انجام شد؛۱۴۲۰ directory فقط در clone دارای owner-label/ID معتبر اصلاح، رویهٔ خصوصی استخراج نیز اصلاح، سپس HTTP و rollback کامل پاس شدند. این خطای restore بود؛ تغییر مجوز یا مالکیت در production انجام نشد. checksum و برابری جدول‌های بازیابی پیشین معتبرند، ولی native bootِ root به‌تنهایی پذیرش HTTP نیست.

انتشار زنده همچنان به integration عادی، CI، backup/checksum/drift تازه و smoke عمومی نیاز دارد. abrupt host loss و COMMIT مبهم در این تمرین fault-inject نشدند؛ fail-closed و بررسی خصوصی journal لازم است و بازیابی شبکه/OOB تأیید نشده است.
