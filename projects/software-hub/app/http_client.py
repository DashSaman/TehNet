"""Pinned HTTPS, bounded observations and exact-byte full verification; no redirects."""
from datetime import datetime,timezone
import hashlib
import http.client
import ipaddress
import re
import socket
import ssl
import threading
import time
from urllib.parse import urlsplit
from .models import HttpObservation,ProbeResult
from .netguard import validate_target,resolve_addresses,TargetRejected
from .health import BudgetDenied

class FetchRejected(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self,target,timeout_seconds,*,context=None):
        context=context or ssl.create_default_context()
        if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:
            raise ValueError('TLS hostname and chain verification required')
        super().__init__(target.hostname,target.port,timeout=timeout_seconds,context=context)
        self.target=target
    def connect(self):
        try:
            self.sock=socket.create_connection((self.target.connected_ip,self.target.port),timeout=self.timeout)
            if ipaddress.ip_address(self.sock.getpeername()[0])!=ipaddress.ip_address(self.target.connected_ip):
                raise OSError('PINNED_PEER_MISMATCH')
            self.sock=self._context.wrap_socket(self.sock,server_hostname=self.target.hostname,do_handshake_on_connect=False)
            self.sock.do_handshake()
        except BaseException:
            self.close();raise

def abort(connection):
    try:
        if connection.sock is not None:connection.sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
    finally:connection.close()

def retry_after(reply):
    value=reply.getheader('Retry-After','')
    if value.isdigit() and len(value)<=10:return min(int(value),86400)
    try:
        from email.utils import parsedate_to_datetime
        return min(max((parsedate_to_datetime(value)-datetime.now(timezone.utc)).total_seconds(),0),86400)
    except (TypeError,ValueError,OverflowError):return 0

class GuardedClient:
    def __init__(self,budget,*,mode='DOMESTIC_ONLY',resolver=resolve_addresses,connection_factory=PinnedHTTPSConnection):
        self.budget=budget;self.mode=mode;self.resolver=resolver;self.connection_factory=connection_factory
    def _source(self,source):
        if self.mode=='MAINTENANCE' or not source.routing_enabled or source.permission_state!='approved' or not source.approval_evidence:
            raise FetchRejected('SOURCE_DISABLED')
        if self.mode=='DOMESTIC_ONLY' and source.domestic_state!='verified':raise FetchRejected('DOMESTIC_EVIDENCE_REQUIRED')
        if not source.base_url:raise FetchRejected('SOURCE_URL_MISSING')

    def _request(self,source,path,artifact,*,verification_only=False):
        self._source(source)
        full=verification_only
        limit=artifact.size_bytes if full else self.budget.limits.sample_bytes
        try:
            host=urlsplit(source.base_url).hostname
            if not host or host not in source.allowed_hosts:raise FetchRejected('HOST_NOT_ALLOWED')
            ticket=self.budget.reserve(host,limit,full=full)
        except (ValueError,BudgetDenied):raise FetchRejected('NETWORK_BUDGET_OR_TARGET') from None
        connection=None;reply=None;timer=None;success=False;backoff=0
        started=time.monotonic();deadline=started+self.budget.limits.timeout_seconds
        now=lambda:datetime.now(timezone.utc)
        try:
            target=validate_target(source.base_url,path,set(source.allowed_hosts),resolver=self.resolver,timeout_seconds=self.budget.limits.timeout_seconds)
            remaining=deadline-time.monotonic()
            if remaining<=0:raise FetchRejected('TIMEOUT')
            connection=self.connection_factory(target,remaining)
            timer=threading.Timer(remaining,abort,args=(connection,));timer.daemon=True;timer.start()
            headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Software-Guard/0.2'}
            if not full:headers['Range']='bytes=0-'+str(min(max(artifact.size_bytes,1),limit)-1)
            connection.request('GET',urlsplit(target.url).path,headers=headers)
            reply=connection.getresponse();status=reply.status
            observation=lambda count=0,error=None:HttpObservation(checked_at=now(),status=status,connected_ip=target.connected_ip,tls_verified=True,body_bytes=count,error_code=error)
            if status not in [200,206]:
                backoff=retry_after(reply)
                if full:raise FetchRejected('HTTP_'+str(status))
                success=status in [404,410]
                return ProbeResult(source_id=source.id,state='absent' if success else 'unknown',checked_at=now(),observation=observation(error='HTTP_'+str(status)))
            if reply.getheader('Content-Encoding','identity').lower() not in ['','identity']:raise FetchRejected('ENCODING_NOT_ALLOWED')
            length=reply.getheader('Content-Length')
            if length is not None and (not length.isdigit() or len(length)>20 or (full and int(length)!=artifact.size_bytes)):raise FetchRejected('SIZE_MISMATCH')
            if full and status!=200:raise FetchRejected('UNEXPECTED_PARTIAL_BODY')
            if not full:
                body=bytearray()
                while len(body)<limit:
                    if time.monotonic()>deadline:raise FetchRejected('TIMEOUT')
                    chunk=reply.read1(min(65536,limit-len(body)))
                    if not chunk:break
                    body.extend(chunk)
                html=bytes(body[:512]).lstrip().lower().startswith((b'<!doctype html',b'<html'))
                coherent=True
                if status==206:
                    expected=min(limit,artifact.size_bytes)
                    match=re.fullmatch(r'bytes 0-(\d{1,20})/(\d{1,20})',reply.getheader('Content-Range',''))
                    coherent=bool(match and int(match[1])+1==expected and int(match[2])==artifact.size_bytes and len(body)==expected and length is not None and int(length)==expected)
                success=not html and coherent
                return ProbeResult(source_id=source.id,state='present_unverified' if success else 'unknown',checked_at=now(),full_hash_verified=False,observation=observation(len(body),None if success else 'BODY_OR_RANGE_INVALID'))
            digest=hashlib.sha256();count=0;prefix=bytearray()
            while True:
                if time.monotonic()>deadline:raise FetchRejected('TIMEOUT')
                chunk=reply.read1(min(65536,artifact.size_bytes-count+1))
                if not chunk:break
                count+=len(chunk)
                if count>artifact.size_bytes:raise FetchRejected('SIZE_MISMATCH')
                if len(prefix)<512:prefix.extend(chunk[:512-len(prefix)])
                digest.update(chunk)
            if prefix.lstrip().lower().startswith((b'<!doctype html',b'<html')):raise FetchRejected('UNEXPECTED_HTML')
            if count!=artifact.size_bytes or digest.hexdigest()!=artifact.sha256:raise FetchRejected('INTEGRITY_MISMATCH')
            success=True
            return ProbeResult(source_id=source.id,state='present_verified',checked_at=now(),full_hash_verified=True,observation=observation(count))
        except (TargetRejected,ssl.SSLError,OSError,http.client.HTTPException,TimeoutError) as exc:
            code='TLS_FAILED' if isinstance(exc,ssl.SSLError) else 'TARGET_OR_TRANSPORT_FAILED'
            raise FetchRejected(code) from None
        finally:
            if timer:timer.cancel()
            if reply:reply.close()
            if connection:connection.close()
            self.budget.finish(ticket,success,retry_after=backoff)
    def probe(self,source,path,artifact):
        try:return self._request(source,path,artifact)
        except FetchRejected as exc:
            now=datetime.now(timezone.utc)
            return ProbeResult(source_id=source.id,state='unknown',checked_at=now,observation=HttpObservation(checked_at=now,error_code=exc.code))
    def verify_remote(self,source,path,artifact):
        """Hash the complete bounded stream; discard chunks immediately, never spool."""
        return self._request(source,path,artifact,verification_only=True)
