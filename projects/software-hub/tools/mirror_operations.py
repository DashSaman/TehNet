"""Operator-only atomic metadata refresh. Payload chunks are verified and discarded."""
import argparse,ipaddress,json,os,sqlite3,tempfile,time
from contextlib import closing
from pathlib import Path
from app.models import SourceConfig,Artifact
from app.external_storage import ExternalRegistry
from app.storage import open_regular,safe_path
from app.http_client import GuardedClient
from app.health import NetworkBudget

def load_manifest(path):
    with open_regular(path) as f:raw=f.read(65537)
    if len(raw)>65536:raise ValueError('Manifest cap exceeded')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('Duplicate field')
            out[k]=v
        return out
    value=json.loads(raw,object_pairs_hook=unique)
    if set(value)!={'format','entries'} or type(value['format'])!=int or value['format']!=1 or not isinstance(value['entries'],list) or not 1<=len(value['entries'])<=5:raise ValueError('Unsupported mirror manifest')
    seen=set()
    for entry in value['entries']:
        if set(entry)!={'source','artifact','relative_path','license_evidence','identity_evidence','approved_cidrs'}:raise ValueError('Unexpected mirror fields')
        item=Artifact.model_validate(entry['artifact']);source=SourceConfig.model_validate(entry['source'])
        if item.visibility!='public' or source.visibility!='public' or not source.routing_enabled or item.sha256 in seen:raise ValueError('Only unique approved public identities')
        for k in ['license_evidence','identity_evidence']:
            if not isinstance(entry[k],str) or not entry[k].startswith('https://') or not 1<=len(entry[k])<=900:raise ValueError('Reviewed references required')
        seen.add(item.sha256)
        approved_networks(entry)
    return value['entries']

def approved_networks(entry):
    values=entry['approved_cidrs']
    if not isinstance(values,list) or not 1<=len(values)<=4:raise ValueError('Exact approved network list required')
    networks=[ipaddress.ip_network(value) for value in values]
    if any(not n.network_address.is_global or n.prefixlen<(16 if n.version==4 else 32) for n in networks):raise ValueError('Bounded public allocations only')
    return networks

class ApprovedPeerClient:
    def __init__(self,client,networks):self.client=client;self.networks=networks;self.observation=None
    def verify_remote(self,*args):
        started=time.monotonic()
        result=self.client.verify_remote(*args)
        peer=ipaddress.ip_address(result.observation.connected_ip)
        if not any(peer in network for network in self.networks):raise ValueError('Verification peer outside reviewed allocations')
        self.observation={'peer_ip':str(peer),'tls_verified':result.observation.tls_verified,'bytes':result.observation.body_bytes,'checked_at_utc':result.checked_at.isoformat(),'elapsed_seconds':round(time.monotonic()-started,3)}
        return result

def refresh(entries,public_root,budget,*,client=None):
    store=ExternalRegistry(safe_path(public_root),visibility='public')
    client=client or GuardedClient(budget)
    owner=store.database.stat()
    observations=[]
    # This private temporary directory contains SQLite metadata only; never payloads.
    with tempfile.TemporaryDirectory(prefix='.metadata-refresh-',dir=store.root) as temporary:
        stage=ExternalRegistry(Path(temporary),visibility='public')
        with store.connection() as original,closing(sqlite3.connect(stage.database)) as snapshot:original.backup(snapshot)
        for index,entry in enumerate(entries):
            if index:time.sleep(1.05)
            checked=ApprovedPeerClient(client,approved_networks(entry))
            stage.register_verified(SourceConfig.model_validate(entry['source']),entry['relative_path'],Artifact.model_validate(entry['artifact']),checked,license_approved=True,provenance=entry['identity_evidence']+' ; '+entry['license_evidence'])
            observations.append({'sha256':entry['artifact']['sha256'],**checked.observation})
        with stage.connection() as db:
            if db.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('Staging integrity failed')
        os.chmod(stage.database,0o600)
        if os.name=='posix':os.chown(stage.database,owner.st_uid,owner.st_gid)
        with stage.database.open('r+b') as f:os.fsync(f.fileno())
        os.replace(stage.database,store.database)
        if os.name=='posix':
            fd=os.open(store.root,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
    return {'updated':len(entries),'payload_files_written':0,'publication':'atomic-metadata','verified_sha256':[e['artifact']['sha256'] for e in entries],'verification':observations}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--public-root',type=Path,required=True);parser.add_argument('--ops-root',type=Path,required=True)
    args=parser.parse_args()
    # Caller must hold the same operation lock as deployment and password setup.
    result=refresh(load_manifest(args.manifest),args.public_root,NetworkBudget(args.ops_root/'network.sqlite'))
    print(json.dumps(result))
if __name__=='__main__':main()
