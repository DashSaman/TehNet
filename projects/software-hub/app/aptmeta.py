"""W4 native Ubuntu signature/date contract; no web mutation or payload storage."""
from pathlib import Path
from .models import VerifiedRelease
from tools.offline_kit import verified_release

def verify_inrelease(path:Path,keyring:Path,**policy)->VerifiedRelease:
    record=verified_release(path,keyring,**policy)
    return VerifiedRelease(suite=record['suite'],inrelease_sha256=record['inrelease_sha256'],release_date=record['date'],valid_until=record['valid_until'])
