<?php
/** Fixed public educational aid; no input, database or WordPress bootstrap. */
header('X-Robots-Tag: noindex, nofollow');
header('X-Content-Type-Options: nosniff');
header('Content-Type: text/csv; charset=UTF-8');
header('Content-Disposition: attachment; filename="business-server-planning-guide-2.csv"');
echo '﻿"گزینهٔ نامزد","چه پرسشی را حل می‌کند؟","وابستگی که باید بررسی شود","از چه نتیجه‌ای پرهیز کنیم؟"
"سرویس روی میزبان موجود","آیا می‌توان از دارایی فعلی استفاده کرد؟","ظرفیت، سلامت، سازگاری و مجوز","موجودبودن یعنی کافی‌بودن نیست"
"VM روی میزبان مناسب","آیا تفکیک و مدیریت workloadها مفید است؟","منابع فیزیکی، ذخیره‌سازی، شبکه و بستر پشتیبانی","VM سخت‌افزار فیزیکی را حذف نمی‌کند"
"میزبان یا محیط مستقل","آیا مرز خرابی/مدیریت جدا لازم است؟","هزینهٔ تهیه و نگهداری و بازیابی","استقلال اسمی، اثبات تداوم سرویس نیست"
';
