import unittest
from pprint import pprint

from cubectl.src.models import ProcessState
from cubectl.src.models import ProcessStatus
from cubectl.src.service_process.service_process import ServiceProcess


class TestServiceProcessBasic(unittest.TestCase):
    init_config_ok = {
        'name': 'test_process',
        'executor': 'python',
        'file': 'assets/example_services/example_service_0.py',
        'arguments': {'--name': 'new_name'}
    }

    init_config_ng = {
        'name': 'test_process',
        'executor': 'python',
        'file': 'not_existing_example_services/example_service_0.py',
        'arguments': {'--name': 'new_name'}
    }

    def test_start_stop_process(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        self.assertEqual(pr.state, ProcessState.stopped)
        pr.start()
        self.assertEqual(pr.state, ProcessState.started)
        pr.stop()
        self.assertEqual(pr.state, ProcessState.stopped)

    def test_stop_process(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        self.assertEqual(pr.state, ProcessState.stopped)
        pr.stop()
        self.assertEqual(pr.state, ProcessState.stopped)

    def _test_try_start_not_existing(self):
        pr = ServiceProcess(init_config=self.init_config_ng)
        pr.start()
        self.assertEqual(ProcessState.failed_start_loop, pr.state)
        pr.stop()

    def test_restart_process(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        pid_before = pr.pid
        pr.restart()
        pid_after = pr.pid
        pr.stop()
        self.assertNotEqual(pid_before, pid_after)

    def test_compare_and_apply_status(self):
        """
        'init_config': {
            'command': 'python example_services/example_service_0.py',
            'dotenv': True,
            'env_files': [],
            'environment': {},
            'name': 'test_process',
            'service': True
        },
        'service_data': {'nginx_config': '', 'port': 123456789},
        'system_data': {'error_code': None, 'pid': 503285, 'state': 'STARTED'}}
        """
        init_config = self.init_config_ok.copy()
        init_config['name'] = 'foobar'

        desired_status = ProcessStatus(
            init_config=init_config,
            service_data={},
            system_data={'state': ProcessState.started}
        )

        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        self.assertEqual(pr.status().init_config.name, self.init_config_ok['name'])

        pr.apply_status(desired_status=desired_status)
        self.assertEqual(pr.status().init_config.name, init_config['name'])
        pr.stop()

    def test_compare_and_apply_status_stop_process(self):
        init_config = self.init_config_ok.copy()

        desired_status = ProcessStatus(
            init_config=init_config,
            service_data={},
            system_data={'state': ProcessState.stopped}
        )

        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        self.assertEqual(pr.state, ProcessState.started)

        pr.apply_status(desired_status=desired_status)
        self.assertEqual(pr.state, ProcessState.stopped)
        pr.stop()

    def test_print_status(self):
        pr = ServiceProcess(init_config=self.init_config_ok)
        pr.start()
        # pprint(pr.status().dict())
        pr.stop()
