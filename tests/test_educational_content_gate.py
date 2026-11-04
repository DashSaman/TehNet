import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('educational_gate', ROOT / 'tools/educational_content_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class EducationalIntegrity(unittest.TestCase):
    def setUp(self):
        directory = ROOT / gate.DIRECTORY
        self.manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        self.ledger = json.loads((ROOT / 'seo/mtcna-video-evidence-2026-11-04.json').read_text(encoding='utf-8'))
        self.bodies = {t['content_file']: (directory / t['content_file']).read_text(encoding='utf-8') for t in self.manifest['targets']}

    def check(self):
        return gate.validate(self.manifest, self.ledger, self.bodies)

    def test_current_correction_is_acceptable_without_claiming_video_review_complete(self):
        self.assertEqual(self.check(), [])
        self.assertTrue(all(v['status'] == 'UNVERIFIED' for v in self.ledger['videos']))

    def test_queue_cannot_regain_an_unverified_video_even_with_an_updated_digest(self):
        body = self.bodies['queues-troubleshooting.html'] + '<a href="https://youtu.be/I_8T6nu8JNg">video</a>'
        self.bodies['queues-troubleshooting.html'] = body
        target = next(t for t in self.manifest['targets'] if t['id'] == 67)
        target['content_sha256_lf'] = gate.hashlib.sha256(body.encode()).hexdigest()
        self.assertIn('Unverified direct lesson-video association', self.check())

    def test_removing_the_role_notice_is_rejected(self):
        self.bodies['routeros-winbox.html'] = self.bodies['routeros-winbox.html'].replace('آموزش نوشتاری مستقل', '')
        self.assertIn('Visible written/supplemental role is required', self.check())

    def test_auto_captions_do_not_silently_become_verified_teaching(self):
        video = self.ledger['videos'][0]
        video.update(status='VERIFIED', claims=[{'topic': 'Queue', 'start_seconds': 12, 'evidence_method': 'auto_captions'}])
        self.assertIn('Verified video requires topic evidence and editorial approval', self.check())
        self.assertIn('A topic/time claim needs a real review reference', self.check())

    def test_missing_source_and_repurposed_identity_are_rejected(self):
        self.ledger['videos'].pop()
        self.manifest['targets'][0]['id'] = 8
        self.assertIn('The seven recordings and GNS3 source must be inventoried', self.check())
        self.assertIn('Exactly the eight existing educational identities are required', self.check())


if __name__ == '__main__':
    unittest.main()
