"""Safe metadata file access; software payload persistence is deliberately absent."""
import os
from pathlib import Path
import re
import stat
class StoreRejected(ValueError):pass
class AccessDenied(Exception):pass
DIGEST=re.compile(r'^[0-9a-f]{64}$')
FILENAME=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._+\-]{0,159}$')
def safe_path(path):
    path=Path(path).absolute()
    if any(p.is_symlink() for p in [path,*path.parents]):raise StoreRejected('Symlink path rejected')
    return path

def open_regular(path):
    path=safe_path(path)
    descriptor=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_BINARY',0))
    try:
        info=os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:raise StoreRejected('Only unlinked-alias regular files are allowed')
        return os.fdopen(descriptor,'rb')
    except BaseException:os.close(descriptor);raise
