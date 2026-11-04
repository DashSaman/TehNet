"""Validate the bounded course correction and evidence-backed video attribution.

This is a repository/release-input gate, not a WordPress admin-save hook.
"""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'content/educational-integrity-2026-11-04'
IDS = {40, 62, 63, 64, 65, 66, 67, 70}
VIDEO_IDS = {'Wbj3C0g__zw', 'a0JMhBdNNgs', 'hqjjvQoO7as', 'Z5EWfUn1Ejw',
             'LO4m55Hf-do', 'XRIMAowqdM4', 'I_8T6nu8JNg', 'OgypQcQS3FA'}


def validate(manifest, ledger, bodies):
    errors = []
    targets = manifest.get('targets', [])
    if len(targets) != 8 or {t.get('id') for t in targets} != IDS:
        errors.append('Exactly the eight existing educational identities are required')
    videos = ledger.get('videos', [])
    if len(videos) != 8 or {v.get('id') for v in videos} != VIDEO_IDS:
        errors.append('The seven recordings and GNS3 source must be inventoried')
    for video in videos:
        if video.get('status') not in ('UNVERIFIED', 'VERIFIED', 'NOT_TAUGHT'):
            errors.append('Unknown verification state')
        claims = video.get('claims', [])
        if video.get('status') == 'VERIFIED' and (not claims or not video.get('reviewer') or not video.get('editor_approval')):
            errors.append('Verified video requires topic evidence and editorial approval')
        for claim in claims:
            if (not isinstance(claim.get('start_seconds'), int) or claim['start_seconds'] < 0
                    or not claim.get('topic') or claim.get('evidence_method') not in ('audio_screen_review', 'instructor_confirmation')
                    or not claim.get('evidence_reference')):
                errors.append('A topic/time claim needs a real review reference')
    for target in targets:
        body = bodies.get(target.get('content_file'), '')
        if not body or hashlib.sha256(body.encode()).hexdigest() != target.get('content_sha256_lf'):
            errors.append('Immutable body digest mismatch')
        if re.search(r'<h1\b|VideoObject|\[video', body, re.I):
            errors.append('Course article must not add a second H1 or unsupported video schema')
        identity = target.get('id')
        role = 'آموزش نوشتاری مستقل' if identity in (62, 63, 64, 65, 66) else 'تکمیلی مستقل'
        if role not in body:
            errors.append('Visible written/supplemental role is required')
        if identity in (62, 63, 64, 65, 66, 67) and re.search(r'youtu(?:be\.com|\.be)', body, re.I):
            errors.append('Unverified direct lesson-video association')
        if identity == 67 and ('خارج از جلسات ضبط‌شده' not in body or 'تدریس نشده' not in body):
            errors.append('Queue must remain explicitly outside the recorded teaching')
    hub = bodies.get('mtcna.html', '')
    if any(v not in hub for v in VIDEO_IDS):
        errors.append('Preserve access to every original recording')
    return errors


def main():
    directory = ROOT / DIRECTORY
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    ledger = json.loads((ROOT / 'seo/mtcna-video-evidence-2026-11-04.json').read_text(encoding='utf-8'))
    bodies = {t['content_file']: (directory / t['content_file']).read_text(encoding='utf-8') for t in manifest['targets']}
    errors = validate(manifest, ledger, bodies)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('EDUCATIONAL_CONTENT_GATE=PASS targets=8 videos=8; video review completion is separate')


if __name__ == '__main__':
    main()
