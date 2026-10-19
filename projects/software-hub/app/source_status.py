"""Explicit public projection of dated, manual source checks; never routing policy."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json

OBSERVATIONS=Path(__file__).resolve().parents[1]/'catalog/source-observations.json'
LABELS={
    'signed_metadata_verified':('امضای مخزن تأیید شد','امضای متادیتای noble-updates بررسی شده؛ تأیید نصب همه بسته‌های این منبع نیست.'),
    'endpoint_reachable':('پاسخ HTTPS دریافت شد','نشانی بررسی‌شده پاسخ ۲۰۰ داده؛ دانلود فایل و نصب از این مسیر تأیید نشده است.'),
    'restricted':('دسترسی محدود در آزمون','این نشانی از محل آزمون پاسخ محدودیت دسترسی داده است.'),
    'metadata_rejected':('متادیتای مخزن پذیرفته نشد','پاسخ HTTPS دریافت شد، اما بررسی امضا یا تازگی متادیتای مخزن قبول نشد؛ این مسیر برای نصب پیشنهاد نمی‌شود.'),
    'redirect':('تغییر مسیر در آزمون','نشانی پاسخ تغییر مسیر داده؛ مقصد بدون بررسی پذیرفته نشده است.'),
    'unavailable':('اتصال تأیید نشد','از محل آزمون پاسخ معتبر دریافت نشد؛ این نتیجه به معنی قطع بودن سراسری منبع نیست.'),
    'unmeasured':('فقط سابقه پژوهش','برای این ردیف نتیجه آزمون قابل نمایش ثبت نشده است.'),
    'stale':('بررسی نیازمند به‌روزرسانی','نتیجه قبلی بیش از ۲۴ ساعت قدمت دارد و تأیید دسترسی فعلی نیست.'),
}

def source_assessments(now=None):
    now=now or datetime.now(timezone.utc)
    try:
        if OBSERVATIONS.stat().st_size>131072:return {}
        data=json.loads(OBSERVATIONS.read_text(encoding='utf-8'))
        if data['schema']!=1 or len(data['observations'])>100:return {}
        result={}
        for item in data['observations']:
            state=item['state'];checked=datetime.fromisoformat(item['checked_at'])
            if state not in LABELS or checked.tzinfo is None or checked>now+timedelta(minutes=5):continue
            if now-checked>timedelta(hours=24):state='stale'
            label,detail=LABELS[state]
            result[item['id']]={'state':state,'label':label,'detail':detail,'checked_at':checked.isoformat(timespec='seconds'),
                                'vantage':'سرور خارج از ایران','scope':'امضای متادیتای noble-updates' if state=='signed_metadata_verified' else 'اتصال HTTPS؛ بدون تأیید نصب',
                                'usable_observation':state in {'signed_metadata_verified','endpoint_reachable'}}
        return result
    except (OSError,ValueError,KeyError,TypeError,OverflowError):return {}

def unmeasured():
    label,detail=LABELS['unmeasured']
    return {'state':'unmeasured','label':label,'detail':detail,'checked_at':None,'vantage':None,'scope':'پژوهش','usable_observation':False}
