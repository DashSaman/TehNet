from pathlib import Path
from collections import Counter,defaultdict
import json
root=Path(__file__).resolve().parents[1];folder=root/'seo/audit-2026-10-16';crawl=json.loads((folder/'public-crawl.json').read_text(encoding='utf-8'));native=json.loads((folder/'native-inventory.json').read_text(encoding='utf-8'));pages=crawl['pages'];ok=[x for x in pages if x.get('status')==200];products=[p for p in native['posts']if p['type']=='product']
def nodes(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from nodes(v)
 elif isinstance(x,list):
  for v in x:yield from nodes(v)
schema_types=Counter();ids=Counter();offers=[]
for p in ok:
 for s in p['schemas']:
  for n in nodes(s.get('value')):
   for t in ([n.get('@type')]if isinstance(n.get('@type'),str)else n.get('@type',[])):schema_types[t]+=1
   if n.get('@id'):ids[n['@id']]+=1
   if n.get('@type')=='Offer':offers.append({'page':p['url'],'price':n.get('price'),'currency':n.get('priceCurrency'),'availability':n.get('availability')})
title_groups=defaultdict(list);canonical_groups=defaultdict(list);content_groups=defaultdict(list)
for p in ok:
 title_groups[p['title']].append(p['url'])
 for c in p['canonicals']:canonical_groups[c].append(p['url'])
for p in products:content_groups[p['content_sha256']].append(p['url'])
images=[{'page':p['url'],**i}for p in ok for i in p['images']]
summary={'crawled':len(pages),'discovered':crawl['discovered'],'native_published':len(native['posts']),'native_terms':len(native['terms']),'http_200':len(ok),'non_200':[{'url':p['url'],'status':p.get('status'),'error':p.get('error')}for p in pages if p.get('status')!=200],
 'noindex_count':sum(any('noindex'in r for r in p['robots'])or'noindex'in p['headers'].get('x-robots-tag','')for p in ok),
 'missing_description':[p['url']for p in ok if not any(p['descriptions'])],
 'multiple_description':[p['url']for p in ok if len(p['descriptions'])>1],
 'h1_not_one':[{'url':p['url'],'h1':p['h1']}for p in ok if len(p['h1'])!=1],
 'canonical_not_one':[{'url':p['url'],'canonical':p['canonicals']}for p in ok if len(p['canonicals'])!=1],
 'duplicate_titles':[{ 'title':k,'urls':v}for k,v in title_groups.items()if len(v)>1],
 'shared_canonical':[{ 'canonical':k,'urls':v}for k,v in canonical_groups.items()if len(v)>1],
 'redirected_final_urls':[{'url':p['url'],'final':p['final_url']}for p in ok if p['url']!=p['final_url']],
 'schema_types':dict(schema_types),'invalid_jsonld':[p['url']for p in ok if any(s.get('invalid')for s in p['schemas'])],
 'offers':offers,'missing_og_title_count':sum(not p['og']['title']for p in ok),'missing_og_description_count':sum(not p['og']['description']for p in ok),'missing_og_image_count':sum(not p['og']['image']for p in ok),
 'image_nodes':len(images),'missing_alt_count':sum(i['alt']is None for i in images),'blank_alt_count':sum(i['alt']=='' for i in images),'images_without_dimensions':sum(not i['width']or not i['height']for i in images),
 'main_chars_low':[{'url':p['url'],'chars':p['main_chars']}for p in ok if p['main_chars']<600],
 'product_count':len(products),'reviewed_spin_products':sum(p['media']['spin_reviewed']=='yes'for p in products),'spin_frames_present':sum(bool(p['media']['spin_ids'])for p in products),'product_content_groups':[{'sha256':k,'count':len(v),'urls':v}for k,v in content_groups.items()],
 'author_nodes_count':sum(bool(p['author_nodes'])for p in ok),'date_nodes_count':sum(bool(p['dates'])for p in ok),'analytics_pages':sum(bool(p['analytics_scripts'])for p in ok),
 'native_posts_not_crawled':[p['url']for p in native['posts']if p['url']not in [x['url']for x in pages]],'runtime_files':native['runtime_files'],
 'mobile_rendered':len(crawl['rendered_mobile']),'mobile_overflow':sum(p.get('overflow',False)for p in crawl['rendered_mobile'])}
unique={p['final_url']:p for p in ok};summary['unique_final_http200_pages']=len(unique);summary['unique_missing_description']=sum(not any(p['descriptions'])for p in unique.values());summary['unique_noindex']=sum(any('noindex'in r for r in p['robots'])for p in unique.values());summary['unique_missing_og_image']=sum(not p['og']['image']for p in unique.values())
summary['utility_endpoint_404']=[p['url']for p in pages if p.get('status')==404 and '/cdn-cgi/'in p['url']]
summary['product_duplicate_title_groups']=[v for v in summary['duplicate_titles']if all('/product/'in u for u in v['urls'])]
# Retain only public diagnostic headers; never archive anonymous session cookies.
for p in crawl['support']:p['headers']={k:v for k,v in p.get('headers',{}).items()if k in ['content-type','x-robots-tag','cache-control']}
(folder/'public-crawl.json').write_text(json.dumps(crawl,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(folder/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
compact={k:summary[k]for k in ['crawled','native_published','native_terms','unique_final_http200_pages','unique_missing_description','unique_noindex','reviewed_spin_products','mobile_rendered','mobile_overflow']};compact['product_content_group_counts']=[x['count']for x in summary['product_content_groups']];compact['product_duplicate_title_groups']=len(summary['product_duplicate_title_groups']);print(json.dumps(compact,ensure_ascii=True))
