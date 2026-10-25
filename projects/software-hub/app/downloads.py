"""Registered external redirects; no website payload files or cache."""
from fastapi import Depends,HTTPException,Query,Request
from fastapi.responses import RedirectResponse
from .access import require_restricted_access
from .models import Artifact,public_projection
from .storage import DIGEST,FILENAME,StoreRejected

def public_catalog(store,q='',cursor=0,limit=50):
    result=store.list_artifacts(q,cursor,limit) if store else {'items':[],'total':0}
    result['items']=[public_projection(Artifact.model_validate(row)).model_dump() for row in result['items']]
    return result

def deliver(request,store,digest,filename,*,context=None):
    if store is None or not DIGEST.fullmatch(digest) or not FILENAME.fullmatch(filename):raise HTTPException(404,'Not Found')
    artifact=store.artifact(digest,context=context)
    if artifact is None or filename!=artifact.filename:raise HTTPException(404,'Not Found')
    try:target=store.download_target(digest,context=context)
    except StoreRejected:raise HTTPException(503,'External object unavailable') from None
    # Public redirects expose their destination. Restricted registries always refuse them.
    return RedirectResponse(target,status_code=307)

def install_public_downloads(site,store):
    @site.get('/v1/artifacts')
    def artifacts(q:str=Query('',max_length=120),cursor:int=Query(0,ge=0,le=10000),limit:int=Query(50,ge=1,le=100)):
        return public_catalog(store,q,cursor,limit)
    @site.get('/v1/artifacts/{digest}')
    def artifact(digest:str):
        if store is None or not DIGEST.fullmatch(digest):raise HTTPException(404,'Not Found')
        item=store.artifact(digest)
        if item is None:raise HTTPException(404,'Not Found')
        return public_projection(item)
    @site.get('/download/{digest}/{filename}')
    @site.head('/download/{digest}/{filename}',include_in_schema=False)
    def download(request:Request,digest:str,filename:str):return deliver(request,store,digest,filename)

def install_private_downloads(router,store):
    @router.api_route('/download/{digest}/{filename}',methods=['GET','HEAD'])
    def download(request:Request,digest:str,filename:str,context=Depends(require_restricted_access)):
        return deliver(request,store,digest,filename,context=context)
