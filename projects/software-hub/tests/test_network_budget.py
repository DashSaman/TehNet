from pathlib import Path
import tempfile
import unittest
from app.health import NetworkBudget,BudgetDenied
from app.models import ProbeBudget

class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'budget.sqlite';self.now=1000000.
        self.budget=NetworkBudget(self.path,ProbeBudget(requests_per_day=20,full_bytes_per_day=100),clock=lambda:self.now)
        self.budget.initialize()
    def test_requests_bytes_and_host_interval_survive_restart(self):
        ticket=self.budget.reserve('mirror.example',60,full=True);self.budget.finish(ticket,True)
        other=NetworkBudget(self.path,self.budget.limits,clock=lambda:self.now)
        with self.assertRaises(BudgetDenied):other.reserve('mirror.example',1,full=True)
        self.now+=1
        with self.assertRaises(BudgetDenied):other.reserve('mirror.example',41,full=True)
    def test_single_full_worker_and_one_per_host(self):
        ticket=self.budget.reserve('one.example',1,full=True);self.now+=1
        with self.assertRaises(BudgetDenied):self.budget.reserve('two.example',1,full=True)
        with self.assertRaises(BudgetDenied):self.budget.reserve('one.example',1)
        self.budget.finish(ticket,True);self.now+=1
        second=self.budget.reserve('two.example',1,full=True);self.budget.finish(second,True)
    def test_global_concurrency_is_bounded(self):
        tickets=[self.budget.reserve(str(n)+'.example',1) for n in range(4)]
        with self.assertRaises(BudgetDenied):self.budget.reserve('fifth.example',1)
        for ticket in tickets:self.budget.finish(ticket,True)
    def test_circuit_breaker_retry_after_and_recovery(self):
        for _ in range(3):
            t=self.budget.reserve('mirror.example',1);self.budget.finish(t,False);self.now+=1
        with self.assertRaises(BudgetDenied):self.budget.reserve('mirror.example',1)
        self.now+=301;t=self.budget.reserve('mirror.example',1);self.budget.finish(t,True)
        self.now+=1;t=self.budget.reserve('mirror.example',1);self.budget.finish(t,True,retry_after=60)
        self.now+=1
        with self.assertRaises(BudgetDenied):self.budget.reserve('mirror.example',1)
    def test_daily_count_and_oversized_request_denied(self):
        for _ in range(20):
            t=self.budget.reserve('mirror.example',1);self.budget.finish(t,True);self.now+=1
        with self.assertRaises(BudgetDenied):self.budget.reserve('mirror.example',1)
        self.now+=86400
        t=self.budget.reserve('mirror.example',1);self.budget.finish(t,True)
        with self.assertRaises(BudgetDenied):self.budget.reserve('x.example',4097)
    def test_expired_worker_lease_cannot_release_new_owner(self):
        old=self.budget.reserve('mirror.example',1,full=True);self.now+=41
        new=self.budget.reserve('mirror.example',1,full=True);self.budget.finish(old,True)
        with self.assertRaises(BudgetDenied):self.budget.reserve('other.example',1,full=True)
        self.budget.finish(new,True)
