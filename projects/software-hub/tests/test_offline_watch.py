from datetime import datetime,timedelta,timezone
import unittest
from tools.offline_watch import assess_operation,assess_window

START=datetime(2026,10,19,13,tzinfo=timezone.utc)

def sample(hours,*,outcome='healthy',publication_hour=1):
    return {'checked_at':(START+timedelta(hours=hours)).isoformat(),'outcome':outcome,
            'accepted_at':(START+timedelta(hours=publication_hour)).isoformat(),'profile_sha256':'a'*64}

class OfflineWatchTests(unittest.TestCase):
    def test_historical_failure_before_last_acceptance_is_not_a_new_incident(self):
        state={'stage':'not_due','accepted_at':START.isoformat(),'checked_at':START.isoformat(),
               'failed_at':(START-timedelta(hours=12)).isoformat(),'last_failure':'ValueError'}
        self.assertEqual(assess_operation(state,START,False),[])
        state['failed_at']=(START+timedelta(minutes=1)).isoformat()
        self.assertIn('unresolved_refresh_failure',assess_operation(state,START+timedelta(minutes=2),False))

    def test_healthy_partial_window_never_claims_elapsed_48_hours(self):
        result=assess_window(START,[sample(0,publication_hour=-6),sample(.5,publication_hour=-6)],START+timedelta(minutes=30))
        self.assertEqual(result['phase'],'observing');self.assertEqual(result['new_publications'],0)

    def test_complete_window_requires_new_in_window_publication_and_coverage(self):
        points=[sample(h/2,publication_hour=-6 if h<3 else 1) for h in range(97)]
        result=assess_window(START,points,START+timedelta(hours=48))
        self.assertEqual(result['phase'],'completed_pass');self.assertEqual(result['new_publications'],1)
        result=assess_window(START,[sample(0),sample(48)],START+timedelta(hours=48))
        self.assertEqual(result['phase'],'completed_incomplete');self.assertIn('observation_gap',result['limitations'])

    def test_old_publication_and_clock_jump_do_not_certify_monitoring(self):
        points=[sample(h/2,publication_hour=-1) for h in range(97)]
        result=assess_window(START,points,START+timedelta(hours=48))
        self.assertEqual(result['phase'],'completed_incomplete');self.assertIn('no_new_publication',result['limitations'])
        with self.assertRaisesRegex(ValueError,'clock'):
            assess_window(START,[sample(1),sample(.5)],START+timedelta(hours=2))

    def test_repaired_incident_is_retained_in_terminal_classification(self):
        points=[sample(h/2,outcome='error' if h==10 else 'healthy') for h in range(97)]
        result=assess_window(START,points,START+timedelta(hours=48))
        self.assertEqual(result['phase'],'completed_with_incidents');self.assertEqual(result['failed_samples'],1)

    def test_deferred_lock_samples_cannot_hide_missing_health_observations(self):
        points=[sample(h/2,outcome='healthy' if h in {0,96} else 'deferred') for h in range(97)]
        result=assess_window(START,points,START+timedelta(hours=48))
        self.assertEqual(result['phase'],'completed_incomplete')
        self.assertEqual(result['maximum_observation_gap_seconds'],48*3600)
