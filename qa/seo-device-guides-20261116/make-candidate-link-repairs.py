# -*- coding: utf-8 -*-
"""TN-CANDIDATE-LINK-REPAIRS-20261116 — candidate repair for the five dead slugs.
Per MANAGER_REVIEW 6925269455: 'drafting a semantically appropriate candidate-link
repair with the correct pinned base is ordinary authorized engineering'. Builds
CANDIDATE patch+proposed pairs from the SAME pinned after-D1 base (a54198ce… /
pages-manifest.json) with ONLY the dead links rerouted to live targets. Accepted
sha-bound artifacts are NOT modified. Status: CANDIDATE / NOT_DEPLOYED.
Run: python -I make-candidate-link-repairs.py  (from qa/seo-device-guides-20261116/)
"""
import difflib, io, json, os, subprocess, sys

QA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QA, '../..'))
PE = os.path.join(ROOT, 'content/seo-device-guides-20261116/page-edits')
CAND = os.path.join(PE, 'candidates')
os.makedirs(CAND, exist_ok=True)

MANIFEST = json.load(io.open(os.path.join(PE, 'pages-manifest.json'), encoding='utf-8'))

# semantic mapping: dead -> LIVE target (documented rationale per row)
MAPPING = [
    {'dead': '/network-support-contract-guide/', 'live': '/services/network-support-tehran/',
     'why': 'راهنمای حذف‌شده (404 در 2026-11-16)؛ مادر خدمت پشتیبانی زنده است و پرسش‌های قرارداد/حجم را پوشش می‌دهد'},
    {'dead': '/services/server-virtualization-tehran/', 'live': '/services/',
     'why': 'زیرصفحهٔ خدمت 404 شده؛ تا تصمیم مالک دربارهٔ بازتولید، لینک به مادر خدمات می‌رود'},
    {'dead': '/network-project-proposal-checklist/', 'live': '/services/network-setup-tehran/',
     'why': 'چک‌لیست پیشنهاد حذف شده؛ جریان پیشنهاد/اجرا در صفحهٔ خدمت راه‌اندازی زنده است'},
    {'dead': '/business-server-planning-guide/', 'live': '/services/network-setup-tehran/',
     'why': 'راهنمای نیازسنجی حذف شده؛ فرگمنت #planning-sheet متعلق به صفحهٔ مرده حذف می‌شود'},
]

def base_content(commit, path):
    return subprocess.run(['git', '-C', ROOT, 'show', commit + ':' + path],
                          capture_output=True, check=True).stdout.decode('utf-8')

pages = []
CONTENT = os.path.join(ROOT, 'content/seo-device-guides-20261116')
for page in MANIFEST['pages']:
    name = page['name']
    accepted_proposed_path = os.path.join(CONTENT, page['proposed'])
    accepted = io.open(accepted_proposed_path, encoding='utf-8').read()
    candidate = accepted
    hits = []
    for m in MAPPING:
        n = candidate.count('" href="' + m['dead']) + candidate.count("href=\"" + m['dead'])
        # count full href occurrences (with or without fragment)
        import re
        n = len(re.findall(re.escape('href="' + m['dead']), candidate))
        if n:
            # replace href only (keep anchor text), drop dead-page fragments
            candidate = re.sub(re.escape('href="' + m['dead']) + r'[^"]*"', 'href="' + m['live'] + '"', candidate)
            hits.append({'dead': m['dead'], 'live': m['live'], 'replaced': n})
    if not hits:
        continue
    commit = None
    import re as _re
    hdr = _re.search(r'^--- a/(.+?)@([0-9a-f]{40}) \(after-D1 ([0-9a-f]{12})…\)', accepted and '', _re.M)
    # read header from accepted patch instead
    acc_patch = io.open(os.path.join(CONTENT, page['patch']), encoding='utf-8').read()
    hdr = _re.search(r'^--- a/(.+?)@([0-9a-f]{40}) \(after-D1 ([0-9a-f]{12})…\)', acc_patch, _re.M)
    base_file, base_commit, prefix = hdr.group(1), hdr.group(2), hdr.group(3)
    base = base_content(base_commit, base_file)
    # candidate unified patch in the same non-strict header style as accepted packets
    rel_name = base_file.rsplit('/', 1)[1]
    diff = difflib.unified_diff(base.splitlines(), candidate.splitlines(),
                                fromfile='--- a/' + base_file + '@' + base_commit + ' (after-D1 ' + prefix + '…)',
                                tofile='+++ b/' + base_file + ' (CANDIDATE-v2, NOT_DEPLOYED)',
                                lineterm='', n=3)
    patch_lines = list(diff)[2:]  # drop difflib's own ---/+++ lines
    patch_text = ('--- a/' + base_file + '@' + base_commit + ' (after-D1 ' + prefix + '…)\n\n'
                  '+++ b/' + base_file + ' (CANDIDATE-v2, NOT_DEPLOYED)\n\n' + '\n'.join(patch_lines) + '\n')
    io.open(os.path.join(CAND, name + '.candidate-v2.patch'), 'w', encoding='utf-8', newline='\n').write(patch_text)
    io.open(os.path.join(CAND, name + '.candidate-v2.proposed.html'), 'w', encoding='utf-8', newline='\n').write(candidate)
    pages.append({'name': name, 'base_commit': base_commit, 'base_file': base_file,
                  'after_d1_sha256': page['after_d1_sha256'], 'replacements': hits,
                  'patch': 'candidates/' + name + '.candidate-v2.patch',
                  'proposed': 'candidates/' + name + '.candidate-v2.proposed.html'})

cand_manifest = {
    'packet': 'TN-CANDIDATE-LINK-REPAIRS-20261116',
    'status': 'CANDIDATE / NOT_DEPLOYED — awaiting manager review; accepted packets untouched',
    'base_note': 'same pinned after-D1 base as pages-manifest.json (a54198ce… commits; per-page after_d1_sha256 identical)',
    'mapping': MAPPING,
    'pages': pages,
}
io.open(os.path.join(CAND, 'candidates-manifest.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(cand_manifest, ensure_ascii=False, indent=1))
import sys
print('CANDIDATE PAGES:', len(pages))
for p in pages:
    print(' ', p['name'], json.dumps(p['replacements'], ensure_ascii=False))
