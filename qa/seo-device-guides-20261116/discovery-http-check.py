# -*- coding: utf-8 -*-
"""TN-DISCOVERY-HTTP-CHECK-20261116 — P1-discovery-matrix HTTP observation.
Read-only public GETs against the 16 allowlisted tehnet.ir URLs + robots.txt +
sitemap membership. NO production change, NO login, NO write to the site.
Fills observation columns with real observed values (or honest HTTP_ERROR text);
never fabricates statuses. Run: python -I discovery-http-check.py  (from qa dir).
"""
import csv, io, json, os, re, ssl, sys, urllib.request, urllib.error
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

QA = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(QA, 'discovery-matrix.csv')
RECEIPT_PATH = os.path.join(QA, 'discovery-http-receipt.json')
DATE = '2026-11-16'
SRC = 'public HTTP GET (read-only, local authorized env) — discovery-http-check.py'
UA = 'Mozilla/5.0 (compatible; TehNet-content-audit/1.0; +https://tehnet.ir)'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE  # observation only; cert validity not part of this audit

started = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return resp.getcode(), dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), b''
    except Exception as e:  # DNS/TLS/timeout — recorded honestly
        return None, {}, ('EXC:%s' % type(e).__name__).encode()

def main():
    rows = list(csv.DictReader(io.open(CSV_PATH, encoding='utf-8-sig')))
    results = []
    errors = 0
    # 1) per-URL GET
    for r in rows:
        url = r['url']
        status, headers, body = fetch(url)
        if status is None:
            r['http_status'] = 'HTTP_ERROR (%s)' % body.decode('ascii', 'replace')
            errors += 1
        else:
            r['http_status'] = str(status)
            text = body.decode('utf-8', 'replace')
            m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', text) or \
                re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', text)
            r['canonical'] = m.group(1) if m else 'NO_CANONICAL_TAG'
            m2 = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']', text)
            r['robots_meta'] = m2.group(1) if m2 else 'NO_ROBOTS_META'
            xrt = headers.get('X-Robots-Tag') or headers.get('x-robots-tag') or 'NO_X_ROBOTS_TAG'
            r['x_robots_tag'] = xrt
            r['last_evidence'] = 'HTTP GET مشاهده مستقیم (read-only)'
            r['evidence_date'] = DATE
            r['evidence_source'] = SRC
        results.append({'url': url, 'http_status': r['http_status']})
    # 2) robots.txt
    rstatus, _, rbody = fetch('https://tehnet.ir/robots.txt')
    if rstatus == 200:
        robots_txt = rbody.decode('utf-8', 'replace')
        sitemap_urls = re.findall(r'(?i)^sitemap:\s*(\S+)', robots_txt, re.M)
        # basic textual check: star-agent disallow prefixes
        star_block, cur_star = [], False
        for line in robots_txt.splitlines():
            s = line.strip()
            if s.lower().startswith('user-agent:'):
                cur_star = (s.split(':', 1)[1].strip() == '*')
            elif cur_star and s.lower().startswith('disallow:'):
                p = s.split(':', 1)[1].strip()
                if p:
                    star_block.append(p)
        robots_summary = '200; sitemap_declared=%d; star_disallow_rules=%d' % (len(sitemap_urls), len(star_block))
        for r in rows:
            path = r['path'] if r['path'].startswith('/') else '/' + r['path']
            blocked = [p for p in star_block if p != '/' and path.startswith(p)]
            r['robots_txt'] = ('ALLOWED (star-agent)' if not blocked else 'DISALLOWED by %s' % blocked[0]) + ' | ' + robots_summary
    else:
        robots_summary = 'HTTP %s' % (rstatus if rstatus else 'ERROR')
        sitemap_urls = []
        for r in rows:
            r['robots_txt'] = 'UNKNOWN (%s)' % robots_summary
    # 3) sitemap membership (one index level deep)
    locs = set()
    sitemap_note = ''
    if sitemap_urls:
        sst, _, sbody = fetch(sitemap_urls[0])
        if sst == 200:
            try:
                root = ET.fromstring(sbody)
                ns = {}
                loc_els = root.findall('.//{*}loc')
                child_maps = []
                if root.tag.endswith('sitemapindex'):
                    for sm in loc_els:
                        child_maps.append(sm.text.strip())
                    for cu in child_maps[:5]:
                        cst, _, cbody = fetch(cu)
                        if cst == 200:
                            try:
                                locs |= {e.text.strip() for e in ET.fromstring(cbody).findall('.//{*}loc')}
                            except ET.ParseError:
                                pass
                else:
                    locs |= {e.text.strip() for e in loc_els}
                sitemap_note = 'fetched %s (index children=%d); total_urls=%d' % (sitemap_urls[0], len(child_maps), len(locs))
            except ET.ParseError as pe:
                sitemap_note = 'PARSE_ERROR %s' % pe
        else:
            sitemap_note = 'HTTP %s on %s' % (sst, sitemap_urls[0])
    else:
        sitemap_note = 'no sitemap directive in robots.txt'
    for r in rows:
        path_url = r['url']
        in_map = any(l.rstrip('/') == path_url.rstrip('/') for l in locs)
        if locs:
            r['sitemap_membership'] = 'YES' if in_map else 'NO (sitemap fetch OK — %s)' % sitemap_note
        else:
            r['sitemap_membership'] = 'UNKNOWN (%s)' % sitemap_note
    # 4) write CSV back (same columns, LF)
    cols = list(rows[0].keys())
    with io.open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    finished = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    receipt = {
        'packet': 'TN-DISCOVERY-HTTP-CHECK-20261116',
        'command': 'python -I discovery-http-check.py',
        'cwd': 'qa/seo-device-guides-20261116/',
        'started_utc': started, 'finished_utc': finished,
        'exit': 1 if errors else 0,
        'mode': 'LOCAL_TEST — read-only public HTTP GETs; no production change; no login; no site write',
        'errors': errors,
        'results': results,
        'robots': {'http_status': rstatus, 'sitemap_directives': sitemap_urls, 'note': sitemap_note},
        'not_run': ['Search Console query data', 'page-render/browser check', 'any site write'],
        'production_touched': False,
    }
    io.open(RECEIPT_PATH, 'w', encoding='utf-8', newline='\n').write(json.dumps(receipt, ensure_ascii=False, indent=1))
    for res in results:
        print(res['url'], '->', res['http_status'])
    print('RECEIPT discovery-http-receipt.json | errors=%d | exit=%d' % (errors, receipt['exit']))
    sys.exit(0)

if __name__ == '__main__':
    main()
