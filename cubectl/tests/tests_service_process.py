import unittest

from cubectl.src.models import ProcessState
from cubectl.src.models import InitProcessConfig
from cubectl.src.service_process.service_process import ServiceProcess


class TestBasic(unittest.TestCase):
    init_config_ok = {
        'name': 'test_process',
        'command': 'python example_services/example_service_0.py'
    }

    init_config_ng = {
        'name': 'test_process',
        'command': 'python ../asdfgbvcwwdefregtrythtrgrfewdergtrhtgrfedfrvice_0.py'
    }

    def test_start_stop_process(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        # status_before = pr.state
        self.assertEqual(pr.state, ProcessState.stopped)
        pr.start()
        # status_before = pr.status()
        self.assertEqual(pr.state, ProcessState.started)
        pr.stop()
        # status_after = pr.status()
        self.assertEqual(pr.state, ProcessState.stopped)

    def test_try_start_not_existing(self):
        pr = ServiceProcess(init_config=self.init_config_ng)
        pr.start()
        self.assertEqual(pr.state, ProcessState.failed_start_loop)
        pr.stop()

    def test_restart_process(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        pid_before = pr.pid
        pr.restart()
        pid_after = pr.pid
        pr.stop()
        self.assertNotEqual(pid_before, pid_after)

    def test_compare_status(self):
        desired_status = {
            'state': str(ProcessState.started)
        }
        # desired_status = None

        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        status = pr.status().dict()
        status.pop('init_config')
        print(status)
        pr.stop()
