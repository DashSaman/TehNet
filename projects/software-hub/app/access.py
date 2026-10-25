"""One server-side authorization boundary; typed contexts alone grant no access."""
from fastapi import HTTPException,Request
from .models import AccessContext,public_projection

SESSION_COOKIE='__Secure-tehnet-software-session'
CHALLENGE_COOKIE='__Secure-tehnet-software-challenge'

def authenticated(request:Request):
    store=request.app.state.auth
    return store.session(request.cookies.get(SESSION_COOKIE)) if store else None

def require_restricted_access(request:Request)->AccessContext:
    context=authenticated(request)
    if context is None:raise HTTPException(404,detail='Not Found')
    return context
