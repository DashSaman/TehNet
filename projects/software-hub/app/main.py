from contextlib import closing
import json
from pathlib import Path
import sqlite3

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import Settings
from .db import open_readonly
from .auth import AuthStore
from .private_routes import install_access
from .external_storage import ExternalRegistry
from .downloads import install_public_downloads,public_catalog

ROOT=Path(__file__).resolve().parents[1]
CAPABILITIES={'public_research':True,'downloads':False,'apt_profile_accepted':False,'restricted_access':False,'rubika':False}
INSTALL_GUIDES=[
    {'id':'curl','title':'cURL','description':'دریافت فایل و بررسی پاسخ سرویس‌های وب از خط فرمان.','package':'curl','check':'curl --version'},
    {'id':'git','title':'Git','description':'دریافت و مدیریت تاریخچه پروژه‌ها و کد.','package':'git','check':'git --version'},
    {'id':'nginx','title':'Nginx','description':'وب‌سرور و پراکسی معکوس. نصب ممکن است سرویس را راه‌اندازی کند؛ اگر وب‌سرور دیگری دارید، ابتدا تداخل پورت را بررسی کنید.','package':'nginx','check':'nginx -v'},
    {'id':'ssh','title':'SSH Client','description':'اتصال امن به سرورهای در دسترس؛ این بسته سرور SSH نصب نمی‌کند.','package':'openssh-client','check':'ssh -V'},
    {'id':'rsync','title':'rsync','description':'همگام‌سازی و انتقال افزایشی فایل‌ها برای پشتیبان‌گیری.','package':'rsync','check':'rsync --version'},
    {'id':'unzip','title':'unzip','description':'نمایش و بازکردن فایل‌های ZIP.','package':'unzip','check':'unzip -v'},
    {'id':'jq','title':'jq','description':'خواندن، فیلترکردن و پردازش خروجی JSON.','package':'jq','check':'jq --version'},
    {'id':'certificates','title':'CA Certificates','description':'گواهی‌های ریشه برای بررسی ارتباط HTTPS؛ بررسی TLS را غیرفعال نکنید.','package':'ca-certificates','check':'dpkg-query -W ca-certificates'},
]


def sources(settings: Settings, q: str, cursor: int, limit: int):
    where="visibility='public' AND instr(lower(provider||' '||ecosystem||' '||id),lower(?))>0"
    with closing(open_readonly(settings.database)) as db:
        count=db.execute('SELECT COUNT(*) FROM sources WHERE '+where,(q,)).fetchone()[0]
        rows=db.execute('SELECT id,provider,ecosystem,config_json FROM sources WHERE '+where+' ORDER BY provider,id LIMIT ? OFFSET ?', (q,limit,cursor)).fetchall()
    items=[]
    for row in rows:
        config=json.loads(row['config_json'])
        # Explicit safe projection; never return stored config, base URL, approvals or private metadata.
        items.append({'id':row['id'],'provider':row['provider'],'ecosystem':row['ecosystem'],
                      'evidence_status':config.get('evidence_status','UNVERIFIED'),
                      'evidence_urls':config.get('evidence_urls',[]),'coverage':config.get('coverage',[]),
                      'routing_enabled':False,'research_date':'2026-10-17'})
    return {'items':items,'total':count,'cursor':cursor,'limit':limit}


def create_app(settings: Settings | None=None) -> FastAPI:
    settings=settings or Settings.from_env()
    app=FastAPI(title='TehNet',docs_url=None,redoc_url=None,openapi_url=None)
    site=FastAPI(title='TehNet Software Archive',version='0.1.0',docs_url=None,redoc_url=None)
    templates=Jinja2Templates(directory=ROOT/'templates')
    auth=AuthStore(settings.auth_dir/'auth.sqlite') if settings.restricted_enabled and settings.auth_dir else None
    site.state.auth=auth
    site.state.settings=settings
    public_store=ExternalRegistry(settings.metadata_dir/'public',visibility='public') if settings.metadata_dir else None
    private_store=ExternalRegistry(settings.metadata_dir/'restricted',authorize=auth.validate_context if auth else None) if settings.metadata_dir else None

    @app.middleware('http')
    async def headers(request, call_next):
        response=await call_next(request)
        response.headers['Cache-Control']='private, no-store'
        response.headers['X-Robots-Tag']='noindex, nofollow'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Vary']='Cookie'
        response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response

    @site.exception_handler(sqlite3.Error)
    @site.exception_handler(ValueError)
    async def unavailable(request, exc):
        return JSONResponse({'error':{'code':'STATE_UNAVAILABLE'}},status_code=503)

    @site.get('/')
    def index(request: Request,q: str=Query('',max_length=120)):
        result=sources(settings,q,0,100)
        return templates.TemplateResponse(request=request,name='index.html',context={
            'prefix':settings.base_path,'result':result,'q':q,'guides':INSTALL_GUIDES,'downloads':public_catalog(public_store)})

    @site.get('/healthz')
    def health(): return {'status':'alive'}

    @site.get('/readyz')
    def ready():
        try:
            with closing(open_readonly(settings.database)) as db:
                db.execute('SELECT id FROM sources LIMIT 1').fetchall()
        except (sqlite3.Error,ValueError):
            return JSONResponse({'status':'unavailable','capabilities':{**CAPABILITIES,'public_research':False}},status_code=503)
        return {'status':'ready','mode':settings.mode,'capabilities':{**CAPABILITIES,'restricted_access':bool(auth and auth.configured),
            'downloads':bool(public_store and public_store.list_artifacts(limit=1)['total'])}}

    @site.get('/v1/sources')
    def list_sources(q: str=Query('',max_length=120),cursor: int=Query(0,ge=0,le=10000),limit: int=Query(50,ge=1,le=100)):
        return sources(settings,q,cursor,limit)

    @site.get('/v1/profiles/noble-core')
    def profile():
        return {'id':'noble-core','state':'planned','accepted':False,'architecture':'amd64',
                'packages':['ca-certificates','curl','git','nginx','openssh-client','rsync','unzip','jq'],
                'installation_policy':'--no-install-recommends','baseline_digest':None,'acceptance_evidence':None}

    install_public_downloads(site,public_store)
    install_access(site,settings,templates,auth,private_store)
    site.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')

    @site.api_route('/{path:path}',methods=['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'],include_in_schema=False)
    def closed(path: str):
        return JSONResponse({'error':{'code':'NOT_FOUND'}},status_code=404)

    app.mount(settings.base_path,site)
    return app


app=create_app()
