from datetime import datetime,timedelta,timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from app.source_status import source_assessments
from tools.probe_research_sources import probe

class SourceStatusTests(unittest.TestCase):
    def check(self,rows,now):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'checks.json';path.write_text(json.dumps({'schema':1,'observations':rows}))
            with patch('app.source_status.OBSERVATIONS',path):return source_assessments(now)

    def test_reachable_endpoint_does_not_claim_install_or_route_approval(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        result=self.check([{'id':'public','state':'endpoint_reachable','checked_at':now.isoformat(),'private_token':'secret','installation_verified':True,'routing_enabled':True}],now)['public']
        self.assertEqual(result['state'],'endpoint_reachable')
        self.assertIn('تأیید نشده',result['detail'])
        self.assertNotIn('secret',json.dumps(result))
        self.assertNotIn('routing_enabled',result)

    def test_stale_future_and_unknown_measurements_never_become_ready(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        rows=[{'id':name,'state':state,'checked_at':time.isoformat()} for name,state,time in [
            ('old','signed_metadata_verified',now-timedelta(hours=25)),('future','endpoint_reachable',now+timedelta(hours=1)),('unknown','made_up',now)]]
        result=self.check(rows,now)
        self.assertEqual(result['old']['state'],'stale');self.assertFalse(result['old']['usable_observation'])
        self.assertNotIn('future',result);self.assertNotIn('unknown',result)

    def test_missing_malformed_file_fails_closed_to_research(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'missing'
            with patch('app.source_status.OBSERVATIONS',path):
                self.assertEqual(source_assessments(),{})
                path.write_text('{broken');self.assertEqual(source_assessments(),{})

    def test_signed_probe_serializes_date_without_install_claim(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        with TemporaryDirectory() as temp:
            with patch('tools.probe_research_sources.fetch_metadata',return_value=({'status':200,'body_is_prefix':False},b'signed fixture')),patch('tools.probe_research_sources.verified_release',return_value={'date':now,'inrelease_sha256':'a'*64,'signers':['b'*40]}),patch('tools.probe_research_sources.tempfile.TemporaryDirectory',side_effect=lambda **kw:TemporaryDirectory(dir=temp)):
                row=probe({'id':'fixture','ecosystem':'apt','base_url':'https://mirror.example/ubuntu/'})
        self.assertEqual(row['state'],'signed_metadata_verified')
        self.assertEqual(row['signed_date'],now.isoformat());json.dumps(row)
        self.assertFalse(row['installation_verified']);self.assertFalse(row['routing_enabled'])

    def test_bad_signature_is_not_promoted_by_reachable_portal(self):
        with TemporaryDirectory() as temp:
            with patch('tools.probe_research_sources.fetch_metadata',return_value=({'status':200,'body_is_prefix':False},b'bad signature')),patch('tools.probe_research_sources.verified_release',side_effect=ValueError('Ubuntu InRelease signature rejected')),patch('tools.probe_research_sources.tempfile.TemporaryDirectory',side_effect=lambda **kw:TemporaryDirectory(dir=temp)):
                row=probe({'id':'fixture','ecosystem':'apt','base_url':'https://mirror.example/ubuntu/'})
        self.assertEqual(row['state'],'metadata_rejected')
        self.assertFalse(row['installation_verified'])

    def test_redirect_is_recorded_without_following_or_http_fallback(self):
        with patch('tools.probe_research_sources.fetch_metadata',return_value=({'status':301,'body_is_prefix':False},b'')) as fetch:
            row=probe({'id':'fixture','ecosystem':'catalog','base_url':'http://mirror.example/'})
        self.assertEqual(row['state'],'redirect');fetch.assert_called_once_with('https://mirror.example/',65536)
        self.assertTrue(row['http_upgraded_to_https'])

if __name__=='__main__':unittest.main()
