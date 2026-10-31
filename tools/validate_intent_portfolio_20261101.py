"""Artifact consistency checks, not semantic/demand/ranking proof."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
import argparse,csv,datetime,hashlib,json,re,unicodedata
R=Path(__file__).resolve().parents[1];SEO=R/'seo'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-receipt',action='store_true');args=parser.parse_args()
rows=list(csv.DictReader((SEO/'topic-portfolio-2026-11-01.csv').open(encoding='utf-8',newline='')))
sources=json.loads((SEO/'content-source-ledger-2026-11-01.json').read_text(encoding='utf-8'));pool={s['id']:s for s in sources['sources']}
inventory=json.loads((SEO/'public-content-inventory-2026-11-01.json').read_text(encoding='utf-8'));live={r['url']for r in inventory['tehnet']}
brand=json.loads((SEO/'brand-intent-map-2026-11-01.json').read_text(encoding='utf-8'));clusters=json.loads((SEO/'topic-clusters-2026-11-01.json').read_text(encoding='utf-8'))['clusters'];cmap={c['id']:c for c in clusters}
checks=[]
def check(label,condition):
 if not condition:raise AssertionError(label)
 checks.append(label)
def normalized(text):return re.sub(r'[\W_]+','',unicodedata.normalize('NFKC',text).replace('ي','ی').replace('ك','ک'))
check('100 candidates, IDs sequential and unique',len(rows)==100 and[r['id']for r in rows]==[f'TN-T{i:03}'for i in range(1,101)])
check('20 clusters with five jobs each',len(clusters)==20 and Counter(r['cluster']for r in rows)==Counter({c['id']:5 for c in clusters}))
check('No exact normalized title or job duplicates',len({normalized(r['title_fa'])for r in rows})==100 and len({normalized(r['reader_job_fa'])for r in rows})==100)
check('No invented publication status',all(r['publication_status']=='CANDIDATE_NOT_PUBLISHED'for r in rows))
check('All rows require further research',all(r['research_status']=='SOURCE_SCOPED_MORE_RESEARCH_REQUIRED'for r in rows))
check('Every topic has scoped sources',all(r['source_ids']and all(s in pool for s in r['source_ids'].split(';'))for r in rows))
check('Sources have publisher/date/depth/scope/limits',all(all(s.get(k)for k in ['publisher','reviewed','review_depth','scope','limits','url'])for s in pool.values()))
check('No source names a tool-inaccessible endpoint as reviewed',all(s['url']not in {x['url']for x in sources['excluded_sources']}for s in pool.values()))
check('TehNet candidates have valid editorial priorities and limits',all(r['owner']=='TehNet'and r['priority']in ['P1','P2','P3']and r['technical_limit_fa']for r in rows))
check('Existing destinations resolve in native published inventory',all(r['preferred_destination']in live for r in rows if r['action']=='EXPAND_EXISTING'))
check('Proposed groups are absent from current inventory',all(r['preferred_destination']not in live and urlparse(r['preferred_destination']).path.startswith('/learn/')for r in rows if r['action']=='PROPOSED_GUIDE_GROUP'))
check('All candidate actions explicit',all(r['action']in ['EXPAND_EXISTING','PROPOSED_GUIDE_GROUP']for r in rows))
check('One action per canonical group',all(len({r['action']for r in rows if r['preferred_destination']==url})==1 for url in {r['preferred_destination']for r in rows}))
check('13 MyTel routes reserved/frozen and existing',len(brand['mytel_existing_frozen'])==13 and {r['url']for r in brand['mytel_existing_frozen']}=={r['url']for r in inventory['mytel']}and all(r['state']=='EXISTING_FROZEN_READ_ONLY'for r in brand['mytel_existing_frozen']))
check('MyTel observed200 and self-canonical',all(r['status']==200 and r['url']==r['final_url']and r['canonical']==[r['url']]and len(r['h1'])==1 for r in inventory['mytel']))
check('MyTel title/H1 preserved in normalized map',all(r['title_observed']==next(x['title']for x in inventory['mytel']if x['url']==r['url'])and r['h1_observed']==' '.join(next(x['h1'][0]for x in inventory['mytel']if x['url']==r['url']).split())for r in brand['mytel_existing_frozen']))
check('Existing commercial TehNet map uses real preferred URLs',len(brand['tehnet_existing'])==6 and all(r['url']in live and r['action']=='IMPROVE_EXISTING_NOT_SYNONYM_PAGE'for r in brand['tehnet_existing']))
check('Candidate destination stays on TehNet, no specialist commercial clone',all(urlparse(r['preferred_destination']).netloc=='tehnet.ir'and urlparse(r['preferred_destination']).path not in {'/'+urlparse(x['url']).path.strip('/')+'/'for x in brand['mytel_existing_frozen']}for r in rows))
check('MyTel reverse referrals are document-only',all(r['state']=='DOCUMENT_ONLY_NOT_DEPLOYED'for r in brand['mytel_referral_proposals']))
queries=json.loads((SEO/'intent-search-observations-2026-11-01.json').read_text(encoding='utf-8'));query_ids={q['id']for q in queries['queries']}
check('All topics have unmeasured or scoped search evidence',all(r['market_evidence']=='UNMEASURED_HYPOTHESIS'or r['market_evidence']in query_ids for r in rows))
paths=['seo/public-content-inventory-2026-11-01.json','seo/content-source-ledger-2026-11-01.json','seo/brand-intent-map-2026-11-01.json','seo/intent-search-observations-2026-11-01.json','seo/topic-clusters-2026-11-01.json','seo/topic-portfolio-2026-11-01.csv']
hashes={p:hashlib.sha256((R/p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()for p in paths}
receipt={'schema':1,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Candidate inventory and cross-brand mapping consistency; no new content publication','status':'VERIFIED_INVENTORY_ONLY','checks_passed':len(checks),'checks':checks,'topics':len(rows),'clusters':len(clusters),'source_rows':len(pool),'source_review_depth':dict(Counter(s['review_depth']for s in pool.values())),'priority_distribution':dict(Counter(r['priority']for r in rows)),'market_evidence_distribution':dict(Counter(r['market_evidence']for r in rows)),'existing_destination_topics':sum(r['action']=='EXPAND_EXISTING'for r in rows),'existing_destinations':len({r['preferred_destination']for r in rows if r['action']=='EXPAND_EXISTING'}),'proposed_canonical_groups':len({r['preferred_destination']for r in rows if r['action']=='PROPOSED_GUIDE_GROUP'}),'mytel_frozen_routes':13,'new_pages_published':0,'new_articles_published':0,'production_writes':0,'source_sha256_lf':hashes,'limits':['Exact duplicate checks do not prove semantic uniqueness; manual reader-job/cluster review also performed','All100 candidates still require full source/command/lab and market/editorial validation before production','No quantitative demand/rank/backlink/GSC cannibalization or AI-citation evidence','Two search observations have uncontrolled provider locale/device; result copies are not verified competitor capability']}
receipt['validator_sha256_lf']=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
if args.write_receipt:
 (R/'qa/growth-2026-10-31/intent-portfolio-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k]for k in ['status','checks_passed','topics','clusters','source_rows','existing_destination_topics','existing_destinations','proposed_canonical_groups','mytel_frozen_routes','new_articles_published']}))
