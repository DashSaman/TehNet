"""Local administrator operations; never exposed as HTTP mutation routes."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import getpass
import hmac
import sys

from .config import Settings
from .db import initialize, snapshot
from .models import SourceConfig,Artifact
from .auth import AuthStore
from .storage import open_regular,FILENAME
from .external_storage import ExternalRegistry
from .health import NetworkBudget
from .http_client import GuardedClient

CATALOG = Path(__file__).resolve().parents[1] / 'catalog/research-sources.json'


def seed_public_research(database: Path) -> None:
    # This checked-in file contains reviewed public mirror research only.
    # Preserve existing rows/approvals/classification; seed is not an updater.
    entries = json.loads(CATALOG.read_text(encoding='utf-8'))['sources']
    with closing(sqlite3.connect(database)) as db:
        for entry in entries:
            source = SourceConfig(id=entry['id'], provider=entry['provider'], ecosystem=entry['ecosystem'],
                                  visibility='public')
            config = json.dumps({key:entry[key] for key in ['evidence_status','evidence_urls','coverage']})
            db.execute('''INSERT INTO sources
                (id,provider,ecosystem,base_url,allowed_hosts_json,config_json,routing_enabled,
                 permission_state,domestic_state,visibility,created_at,updated_at)
                 VALUES (?,?,?,NULL,'[]',?,0,'unreviewed','unverified','public',?,?)
                 ON CONFLICT(id) DO NOTHING''',
                (source.id,source.provider,source.ecosystem,config,'2026-10-17','2026-10-17'))
        db.commit()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init-db','seed-public-research','backup','init-auth','set-password','revoke-sessions','reset-lockout','init-store','init-network','register-external'])
    parser.add_argument('--destination',type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--size',type=int)
    parser.add_argument('--name')
    parser.add_argument('--version')
    parser.add_argument('--architecture')
    parser.add_argument('--filename')
    parser.add_argument('--visibility',choices=['public','restricted'],default='restricted')
    parser.add_argument('--license-approved',action='store_true')
    parser.add_argument('--provenance')
    parser.add_argument('--source-policy',type=Path)
    parser.add_argument('--relative-path')
    args=parser.parse_args()
    settings=Settings.from_env()
    if args.command=='init-db': initialize(settings.database)
    elif args.command=='seed-public-research': seed_public_research(settings.database)
    elif args.command in ['init-auth','set-password','revoke-sessions','reset-lockout']:
        if settings.auth_dir is None:parser.error('Configure a separate TEHNET_SOFTWARE_AUTH directory first')
        auth=AuthStore(settings.auth_dir/'auth.sqlite')
        if args.command=='set-password':
            if not sys.stdin.isatty():parser.error('Password setup requires an interactive terminal; no stdin/argument passwords')
            password=getpass.getpass('New private-section password (16+ characters): ')
            confirmation=getpass.getpass('Confirm password: ')
            if not hmac.compare_digest(password.encode(),confirmation.encode()):parser.error('Passwords do not match')
            auth.initialize();auth.set_password(password)
        elif args.command=='init-auth':auth.initialize()
        elif args.command=='revoke-sessions':auth.revoke_all()
        else:auth.reset_lockout()
    elif args.command=='init-store':
        if settings.metadata_dir is None:parser.error('Configure a separate TEHNET_SOFTWARE_METADATA root')
        for visibility in ['public','restricted']:ExternalRegistry(settings.metadata_dir/visibility,visibility=visibility).initialize()
    elif args.command=='init-network':
        if settings.operation_dir is None:parser.error('Configure a separate TEHNET_SOFTWARE_OPS root')
        NetworkBudget(settings.operation_dir/'network.sqlite').initialize()
    elif args.command=='register-external':
        if settings.metadata_dir is None or not args.license_approved or not args.provenance:parser.error('Metadata root, explicit license approval and provenance required')
        if any(getattr(args,key) is None for key in ['sha256','size','name','version','architecture','filename']):parser.error('Complete trusted artifact metadata required')
        if settings.operation_dir is None or args.source_policy is None or args.relative_path is None:parser.error('Initialized operations, private source policy and registered relative path required')
        item=Artifact(sha256=args.sha256,size_bytes=args.size,name=args.name,version=args.version,architecture=args.architecture,filename=args.filename,visibility=args.visibility)
        with open_regular(args.source_policy) as source:
            raw=source.read(65537)
            if len(raw)>65536:parser.error('Source policy exceeds cap')
            policy=SourceConfig.model_validate_json(raw)
        store=ExternalRegistry(settings.metadata_dir/args.visibility,visibility=args.visibility)
        budget=NetworkBudget(settings.operation_dir/'network.sqlite')
        store.register_verified(policy,args.relative_path,item,GuardedClient(budget,mode=settings.mode),license_approved=True,provenance=args.provenance)
    else:
        if args.destination is None: parser.error('backup needs --destination')
        snapshot(settings.database,args.destination)
    print(args.command+': OK')


if __name__=='__main__': main()
