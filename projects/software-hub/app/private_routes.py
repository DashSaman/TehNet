"""Generic private access flow; no private content enters public responses."""
from urllib.parse import parse_qs
from fastapi import APIRouter,Depends,HTTPException,Request,Query
from fastapi.responses import JSONResponse,RedirectResponse
from starlette.concurrency import run_in_threadpool
from .access import SESSION_COOKIE,CHALLENGE_COOKIE,require_restricted_access
from .auth import AuthDenied,AuthThrottled
from .downloads import install_private_downloads

async def form_fields(request):
    settings=request.app.state.settings
    if request.headers.get('origin')!=settings.public_origin:raise HTTPException(403,'Request denied')
    if request.headers.get('content-type','').split(';')[0].strip()!='application/x-www-form-urlencoded':raise HTTPException(415,'Unsupported request')
    data=bytearray()
    async for chunk in request.stream():
        if len(chunk)>4096-len(data):raise HTTPException(413,'Request too large')
        data.extend(chunk)
    try:
        fields=parse_qs(data.decode('utf-8'),strict_parsing=True,max_num_fields=3,keep_blank_values=True)
    except (ValueError,UnicodeError):raise HTTPException(403,'Request denied')
    if any(k not in ['csrf','password'] or len(v)!=1 for k,v in fields.items()) or not fields.get('csrf'):
        raise HTTPException(403,'Request denied')
    return {k:v[0] for k,v in fields.items()}

def install_access(site,settings,templates,auth,store=None):
    access=APIRouter(prefix='/access',include_in_schema=False)
    private=APIRouter(prefix='/private',dependencies=[Depends(require_restricted_access)],include_in_schema=False)

    def cookie(response,name,value,age):
        response.set_cookie(name,value,max_age=age,path=settings.base_path,secure=True,httponly=True,samesite='strict')

    def clear(response,name):
        response.delete_cookie(name,path=settings.base_path,secure=True,httponly=True,samesite='strict')

    def login_page(request,*,csrf='',available=True,status=200,message=''):
        return templates.TemplateResponse(request=request,name='access.html',context={'prefix':settings.base_path,'csrf':csrf,'available':available,'message':message},status_code=status)

    @access.get('/')
    def login_form(request:Request):
        if not auth or not auth.configured:return login_page(request,available=False,status=503)
        try:nonce,csrf=auth.challenge()
        except AuthThrottled:return JSONResponse({'error':{'code':'TRY_LATER'}},status_code=429,headers={'Retry-After':'60'})
        response=login_page(request,csrf=csrf)
        cookie(response,CHALLENGE_COOKIE,nonce,600)
        return response

    @access.post('/')
    async def login(request:Request):
        fields=await form_fields(request)
        if not auth or not auth.configured:return login_page(request,available=False,status=503)
        if 'password' not in fields:raise HTTPException(403,'Request denied')
        try:
            token,context=await run_in_threadpool(auth.login,request.cookies.get(CHALLENGE_COOKIE),fields['csrf'],fields['password'])
            # Rotate the current browser's session on successful reauthentication.
            await run_in_threadpool(auth.revoke_token,request.cookies.get(SESSION_COOKIE))
        except AuthDenied:
            response=login_page(request,available=False,status=401,message='ورود انجام نشد. فرم ورود را دوباره باز کنید و اطلاعات را بررسی کنید.')
        except AuthThrottled:
            response=login_page(request,available=False,status=429,message='تلاش‌های ورود زیاد است؛ یک دقیقه دیگر دوباره امتحان کنید.')
            response.headers['Retry-After']='60'
        else:
            response=RedirectResponse(settings.base_path+'/private/',status_code=303)
            cookie(response,SESSION_COOKIE,token,3600)
        clear(response,CHALLENGE_COOKIE)
        return response

    @access.post('/logout')
    async def logout(request:Request):
        fields=await form_fields(request)
        try:
            if not auth:raise AuthDenied()
            await run_in_threadpool(auth.logout,request.cookies.get(SESSION_COOKIE),fields['csrf'])
        except AuthDenied:raise HTTPException(403,'Request denied')
        response=RedirectResponse(settings.base_path+'/access/',status_code=303)
        clear(response,SESSION_COOKIE);clear(response,CHALLENGE_COOKIE)
        return response

    @private.get('/')
    def private_home(request:Request,context=Depends(require_restricted_access)):
        result=store.list_artifacts(context=context) if store else {'items':[],'total':0}
        return templates.TemplateResponse(request=request,name='private.html',context={'prefix':settings.base_path,'csrf':auth.csrf(context),'result':result})

    @private.get('/v1/artifacts')
    def private_catalog(q:str=Query('',max_length=120),cursor:int=Query(0,ge=0,le=10000),limit:int=Query(50,ge=1,le=100),context=Depends(require_restricted_access)):
        return store.list_artifacts(q,cursor,limit,context=context) if store else {'items':[],'total':0}

    install_private_downloads(private,store)

    @private.api_route('/{path:path}',methods=['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'])
    def private_unknown(path:str):raise HTTPException(404,'Not Found')

    site.include_router(access);site.include_router(private)
