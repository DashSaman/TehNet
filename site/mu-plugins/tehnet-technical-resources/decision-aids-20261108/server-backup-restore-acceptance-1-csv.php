<?php
/** Fixed public educational aid; no input, database or WordPress bootstrap. */
header('X-Robots-Tag: noindex, nofollow');
header('X-Content-Type-Options: nosniff');
header('Content-Type: text/csv; charset=UTF-8');
header('Content-Disposition: attachment; filename="server-backup-restore-acceptance-1.csv"');
echo '﻿"سرویس","منبع/نسخه","محیط بازیابی","آزمون کاربر مجاز","شاهد","محدودیت","نتیجه"
"UNKNOWN","UNKNOWN","ایزوله و مصوب؛ جزئیات تعیین شود","کار نماینده باید تعریف شود","مرجع خصوصی لازم است","وابستگی‌ها نامعلوم","NOT_TESTED"
"UNKNOWN","UNKNOWN","UNKNOWN","مجوز مثبت و منفی","زمان‌ها و مشاهدهٔ داده","نقطهٔ داده و سازگاری نامعلوم","NOT_TESTED"
';
