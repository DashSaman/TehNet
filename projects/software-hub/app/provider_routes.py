"""Read-only accepted-source selector and client code; no payload proxy/storage."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime,timedelta,timezone
from fastapi import Request
from fastapi.responses import JSONResponse,Response

ROOT=Path(__file__).resolve().parents[1]
RECEIPTS=ROOT/'catalog/provider-qualification.json'
NAMES={'arvan':'ابر آروان','linuxmirrors':'LinuxMirrors.ir','liara':'لیارا','hamravesh':'هم‌روش'}
TOOLS={'git','curl','jq','python','pip','wget','rsync','ssh'}
CLIENT_SHA='fd35d9874932bc35fa8ff026c8608c61ed86533fc46d9ac56d00387e710e0fc9'

def accepted_sources():
    try:
        if RECEIPTS.stat().st_size>131072:return {'providers':[]}
        data=json.loads(RECEIPTS.read_text(encoding='utf-8'));digest=data['profile_sha256']
        if data['format']!=1 or not re.fullmatch('[a-f0-9]{64}',digest):return {'providers':[]}
        accepted=[];seen=set()
        for item in data['providers']:
            identity=item.get('provider');packages=item.get('packages',0)
            if identity not in NAMES or identity in seen or item.get('outcome')!='pass' or item.get('qualified_profile_sha256')!=digest or not 1<=packages<=200:continue
            checks=item.get('negative_checks',{})
            if item.get('complete_hash_verified_downloads')!=packages+6 or set(item.get('functional_tools',[]))!=TOOLS:continue
            if any(checks.get(key,{}).get('exit',0)==0 or checks.get(key,{}).get('dpkg_unchanged') is not True for key in ['corrupt_required_archive','missing_required_archive','forged_signed_metadata','newer_nonseed_dependency']):continue
            if checks.get('clean_offline_install',{}).get('exit')!=0 or checks['clean_offline_install'].get('dpkg_audit')!='empty':continue
            tested=datetime.fromisoformat(item['accepted_at'])
            if tested.tzinfo is None or not re.fullmatch('[a-f0-9]{64}',item['install_evidence_sha256']):continue
            seen.add(identity)
            accepted.append({'provider':identity,'name':NAMES[identity],'accepted_at':tested.astimezone(timezone(timedelta(hours=3,minutes=30))).isoformat(timespec='seconds'),'packages':packages,'functional_tools':sorted(TOOLS),'profile_sha256':digest,'install_evidence_sha256':item['install_evidence_sha256']})
        return {'profile_sha256':digest,'scope':'Dated exact Ubuntu24.04 amd64 devtools kit; direct full-hash downloads and clean offline install,not general mirror/Iran acceptance','providers':accepted}
    except (OSError,ValueError,TypeError,KeyError):return {'providers':[]}

def install_provider_routes(site,settings,templates):
    @site.get('/offline/sources/')
    def selector(request:Request):
        helper=(ROOT/'app/provider_kit.py').read_bytes()
        return templates.TemplateResponse(request=request,name='provider-sources.html',context={'prefix':settings.base_path,'result':accepted_sources(),'helper_sha256':hashlib.sha256(helper).hexdigest(),'client_sha256':CLIENT_SHA})

    @site.get('/offline/sources/acceptance.json')
    def receipts():return JSONResponse(accepted_sources())

    @site.get('/offline/provider_kit.py')
    def helper():return Response((ROOT/'app/provider_kit.py').read_bytes(),media_type='text/plain; charset=utf-8')
