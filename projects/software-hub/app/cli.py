"""Local administrator operations; never exposed as HTTP mutation routes."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .config import Settings
from .db import initialize, snapshot
from .models import SourceConfig

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
    parser.add_argument('command',choices=['init-db','seed-public-research','backup'])
    parser.add_argument('--destination',type=Path)
    args=parser.parse_args()
    settings=Settings.from_env()
    if args.command=='init-db': initialize(settings.database)
    elif args.command=='seed-public-research': seed_public_research(settings.database)
    else:
        if args.destination is None: parser.error('backup needs --destination')
        snapshot(settings.database,args.destination)
    print(args.command+': OK')


if __name__=='__main__': main()
