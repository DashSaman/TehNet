"""Canonical allowlisted HTTPS targets and numeric DNS pinning; never a public proxy."""
import ipaddress
import queue
import re
import socket
import threading
from urllib.parse import unquote,urlsplit,urlunsplit
from .models import ValidatedTarget

class TargetRejected(ValueError):pass

DNS_SLOTS=threading.BoundedSemaphore(4)
def resolve_addresses(host,timeout_seconds):
    # A timed-out OS resolver keeps its slot until it actually finishes.
    # Repeated timeouts cannot create unbounded background resolver threads.
    if not DNS_SLOTS.acquire(blocking=False):raise TargetRejected('DNS_BUSY')
    result=queue.Queue(maxsize=1)
    def lookup():
        try:result.put((True,tuple({row[4][0] for row in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)})))
        except OSError:result.put((False,()))
        finally:DNS_SLOTS.release()
    threading.Thread(target=lookup,daemon=True).start()
    try:ok,addresses=result.get(timeout=timeout_seconds)
    except queue.Empty:raise TargetRejected('DNS_TIMEOUT') from None
    if not ok:raise TargetRejected('DNS_FAILED')
    return addresses

def clean_path(value,*,relative):
    if not value or len(value)>1500 or any(ord(c)<33 or ord(c)>126 for c in value):raise TargetRejected('INVALID_PATH')
    try:decoded=unquote(value,errors='strict')
    except UnicodeError:raise TargetRejected('INVALID_PATH') from None
    if any(x in value.lower() for x in ['%2f','%5c']):raise TargetRejected('AMBIGUOUS_PATH')
    if '%' in decoded or not re.fullmatch(r'[A-Za-z0-9._~+/\-]+',decoded):raise TargetRejected('INVALID_PATH')
    if relative and decoded.startswith('/'):raise TargetRejected('ABSOLUTE_PATH')
    segments=decoded.strip('/').split('/')
    if any(x in ['.','..',''] for x in segments):raise TargetRejected('TRAVERSAL')
    return decoded

def canonical_target(base_url,relative_path,allowed_hosts):
    """Syntax/allowlist only; this is not DNS or availability verification."""
    if not isinstance(base_url,str) or len(base_url)>2000 or any(ord(x)<33 or ord(x)>126 for x in base_url) or '\\' in base_url:
        raise TargetRejected('INVALID_URL')
    try:
        base=urlsplit(base_url);port=base.port or 443;host=base.hostname
    except ValueError:raise TargetRejected('INVALID_URL') from None
    if base.scheme!='https' or base.username is not None or base.password is not None or base.query or base.fragment or port!=443:
        raise TargetRejected('HTTPS_ALLOWLIST_REQUIRED')
    if not host or host.endswith('.') or host not in allowed_hosts or not re.fullmatch(r'[a-z0-9][a-z0-9.\-]{0,252}',host):
        raise TargetRejected('HOST_NOT_ALLOWED')
    root=clean_path(base.path,relative=False).rstrip('/') if base.path not in ['', '/'] else ''
    path=clean_path(relative_path,relative=True)
    return host,urlunsplit(('https',host,root+'/'+path,'',''))

def validate_target(base_url,relative_path,allowed_hosts,*,resolver=resolve_addresses,timeout_seconds=10):
    host,url=canonical_target(base_url,relative_path,allowed_hosts)
    try:
        addresses=tuple(ipaddress.ip_address(a) for a in resolver(host,timeout_seconds))
    except (OSError,ValueError,TimeoutError):raise TargetRejected('DNS_FAILED') from None
    if not addresses or any(not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_unspecified or
        (getattr(ip,'ipv4_mapped',None) is not None and not ip.ipv4_mapped.is_global) for ip in addresses):
        raise TargetRejected('NON_PUBLIC_DNS')
    chosen=sorted(set(addresses),key=lambda ip:(ip.version,ip.packed))[0]
    return ValidatedTarget(url=url,hostname=host,connected_ip=str(chosen),port=443)
