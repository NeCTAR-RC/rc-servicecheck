from test.common import BaseTestCase
from tastypie.exceptions import BadRequest


class MonitoringTestCase(BaseTestCase):

    def test_duplicate(self):
        # Setup a monitoring
        monitoring_json, expected_config = self.setup_monitoring()

        # Run the create action on the monitoring
        self.run_action('create', monitoring_json, expected_config)

        # Adding the same monitoring again must not be allowed
        self.assertRaises(
            BadRequest, self.run_action, 'create', monitoring_json,
            expected_config)

    def setup_monitoring(self):
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

        config = '''define host {
    use                     linux-server
    host_name               google.com
    alias                   google.com
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  1
}

define contact {
    contact_name                    user1-somemail@somedomain.org
    use                             generic-contact
    alias                           someuser
    email                           somemail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          1
}

define contactgroup {
    contactgroup_name       user1-somemail@somedomain.org_GROUP
    alias                   user1-somemail@somedomain.org_GROUP
    members                 user1-somemail@somedomain.org
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")
