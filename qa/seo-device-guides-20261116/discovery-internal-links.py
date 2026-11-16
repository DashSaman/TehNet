# -*- coding: utf-8 -*-
"""TN-DISCOVERY-INTERNAL-LINKS-20261116 — observed internal-link map among the
16 allowlisted tehnet.ir URLs (read-only public GETs). Replaces unverified prose
claims in the internal_backlink column with precise per-page observations:
which live allowlist pages link to which allowlist URLs, and whether any LIVE
page still links to the five dead (404) slugs. Run from qa dir:
python -I discovery-internal-links.py
"""
import csv, io, json, os, re, ssl, sys, urllib.request, urllib.error
from datetime import datetime, timezone

QA = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(QA, 'discovery-matrix.csv')
RECEIPT_PATH = os.path.join(QA, 'internal-links-receipt.json')
DATE = '2026-11-16'
UA = 'Mozilla/5.0 (compatible; TehNet-content-audit/1.0; +https://tehnet.ir)'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

started = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception as e:
        return None, ('EXC:%s' % type(e).__name__).encode()

def main():
    rows = list(csv.DictReader(io.open(CSV_PATH, encoding='utf-8-sig')))
    urls = [r['url'] for r in rows]
    url_set = {u.rstrip('/') for u in urls}
    dead = [r['url'] for r in rows if (r['http_status'] or '').strip() == '404']
    dead_set = {d.rstrip('/') for d in dead}
    live = [r['url'] for r in rows if (r['http_status'] or '').strip() == '200']

    link_map = {}      # target -> set of live source paths linking to it
    dead_outlinks = {} # live source -> dead targets it links to
    for src in live:
        status, body = fetch(src)
        if status != 200:
            link_map.setdefault('__FETCH_ERROR__', set()).add(src)
            continue
        text = body.decode('utf-8', 'replace')
        hrefs = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', text)
        seen = set()
        for h in hrefs:
            h = h.split('#', 1)[0].rstrip('/')
            if not h.startswith('http'):
                if h.startswith('/'):
                    h = 'https://tehnet.ir' + h
                else:
                    continue
            if 'tehnet.ir' not in h:
                continue
            if h in url_set and h != src.rstrip('/'):
                seen.add(h)
            if h in dead_set:
                dead_outlinks.setdefault(src, set()).add(h)
        for t in seen:
            link_map.setdefault(t, set()).add(src.rstrip('/').replace('https://tehnet.ir', '') or '/')

    # update matrix internal_backlink with observed values
    for r in rows:
        u = r['url'].rstrip('/')
        if u in dead_set:
            links_in = sorted(link_map.get(u, set()))
            r['internal_backlink'] = ('LINKED_FROM_LIVE_PAGES: ' + ', '.join(links_in) + ' (observed %s — dead target!)' % DATE) if links_in else 'NO_LINK_FROM_LIVE_ALLOWLIST_PAGES (observed %s)' % DATE
        elif u in live:
            links_in = sorted(link_map.get(u, set()))
            r['internal_backlink'] = ('linked-from: ' + ', '.join(links_in) + ' (observed %s)' % DATE) if links_in else 'no-link-from-other-allowlist-pages (observed %s)' % DATE
        else:
            r['internal_backlink'] = 'UNKNOWN (page not 200 this run)'
    cols = list(rows[0].keys())
    with io.open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        w.writeheader(); [w.writerow(r) for r in rows]

    finished = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    receipt = {
        'packet': 'TN-DISCOVERY-INTERNAL-LINKS-20261116',
        'command': 'python -I discovery-internal-links.py',
        'cwd': 'qa/seo-device-guides-20261116/',
        'started_utc': started, 'finished_utc': finished,
        'exit': 0,
        'mode': 'LOCAL_TEST — read-only public GETs of the 11 live allowlist pages; no site write',
        'link_map_target_to_sources': {k: sorted(v) for k, v in sorted(link_map.items())},
        'live_pages_still_linking_to_dead_slugs': {k: sorted(v) for k, v in sorted(dead_outlinks.items())},
        'not_run': ['full site crawl beyond allowlist pages', 'Search Console', 'any site write'],
        'production_touched': False,
    }
    io.open(RECEIPT_PATH, 'w', encoding='utf-8', newline='\n').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print('LINK_MAP:', json.dumps({k: sorted(v) for k, v in sorted(link_map.items())}, ensure_ascii=False)[:800])
    print('DEAD_OUTLINKS:', json.dumps({k: sorted(v) for k, v in sorted(dead_outlinks.items())}, ensure_ascii=False)[:500])
    print('RECEIPT internal-links-receipt.json | exit=0')
    sys.exit(0)

if __name__ == '__main__':
    main()
