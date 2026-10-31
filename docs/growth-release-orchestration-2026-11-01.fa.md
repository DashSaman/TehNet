# انتشار محدود خدمات و ابزار شبکه

وضعیت اولیه: `IN_PROGRESS`؛ ابزار نوشته شده، چهار boundary test پاس است؛ هنوز تمرین کامل file+content و انتشار production انجام نشده است.

`ops/release-growth-content.py` بسته را از blobهای دو commit کامل می‌سازد: source برای شش فایل و manifest/migration، baseline برای checksum نسخهٔ قبلی. فایل operator نیز از همان source می‌آید. CRLF محیط checkout وارد بسته نمی‌شود. config، bundle اجرایی، log، SQL، نسخهٔ قبلی فایل‌ها و journal فقط در محل خصوصی بیرون Git/webroot می‌مانند. config شامل شناسهٔ دقیق app/DB و حساب CLI موجود است؛ نمونه‌ای حاوی مقدار واقعی در مخزن قرار نمی‌گیرد.

روی میزبان، check/apply/rollback سریالی و تحت flock اجرا می‌شوند. staging باید فقط یک شبکهٔ internal و هیچ port منتشرشده داشته باشد. production فقط جفت container و پورت loopback قبلاً مجاز را می‌پذیرد؛ nonce/index/commerce و مسیر محتوا را migration بومی بررسی می‌کند. marker داخلیِ scope مجوز مالک ایجاد نمی‌کند؛ CI و ادغام عادی، backup/checksum تازه و qualification بازیابی مستقل همچنان لازم‌اند.

ترتیب اعمال: سه module، دو کلاس فرم و در آخر MU loader. هر فایل با temp/fsync/rename و checksum کنترل می‌شود؛ directory تازه برای وب قابل پیمایش است. ترتیب بازگشت: اول migration محتوا، سپس loader و کلاس‌ها، در آخر moduleها. مسیر/نوع فایل و تغییر متعلق به دیگری باعث توقف می‌شود. backupهای فایل پیش از undo کنترل می‌شوند. قفل operator هماهنگی ابزارها را فراهم می‌کند؛ ویرایشگر فایل خارج از این قرارداد باید از تغییر هم‌زمان خودداری کند و این ابزار جای filesystem transaction سراسری را نمی‌گیرد.

خطای مبهم commit محتوا، drift یا journal ناقص، `NEEDS_RECONCILIATION` است؛ فایل‌های لازم برای محتوا نگه داشته می‌شوند. پاک‌کردن journal یا retry کور روش رفع مشکل نیست. فقط APPLIED اثبات‌شده اجازهٔ rollback محتوا می‌دهد؛ نبود journal یا FAILED با check مستقلِ baseline و protected digest باید ثابت شود. تغییر مجاز و هم‌زمان دادهٔ دیگران ممکن است این گیت محافظه‌کارانه را متوقف کند؛ آن داده بازنویسی نمی‌شود.

پذیرش باقی‌مانده: clone تازه و مستقل از backup، check → apply → repeat → HTTP smoke → rollback → repeat، checksum شش فایل، اصل خانه/منو/موجودی/داده، و عدم تغییر runtimeهای موجود. clone قبلیِ editor و DB tmpfs آن بازسازی نمی‌شوند. آزمون ۳۷تایی migration قبلاً پاس شده و با ننوشتن PHP تازه تکرار بی‌دلیل نمی‌شود. نتیجهٔ تمرین و انتشار واقعی باید جدا در رسید مناسب انتشار عمومی ثبت شوند.
