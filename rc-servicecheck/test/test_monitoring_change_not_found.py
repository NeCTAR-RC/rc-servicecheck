from test.common import BaseTestCase
from django.http.response import Http404


class MonitoringTestCase(BaseTestCase):

    def test_change_not_found(self):
        # Setup a monitoring with no expected config
        monitoring_json, expected_config = self.setup_monitoring_1()

        # Run the update action on the monitoring that doesn't exist
        self.assertRaises(
            Http404, self.run_action, 'update', monitoring_json,
            expected_config, 1)

    def setup_monitoring_1(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 1,
                "checks": {
                    "ssh": 0,
                    "http": 0,
                    "https": 0,
                    "smtp": 0,
                    "hdd_usage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpu_load": 0
                },
                "token": '1'
            },
            "contact": {
                "username": 'user1',
                "alias": 'someuser',
                "email": 'somemail@somedomain.org',
                "token": '1'
            },
            "creator": {
                "name": 'creator1',
                "email": 'creator1@email.com'
            }
        }

        return data, ''
