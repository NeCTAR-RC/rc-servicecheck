from test.common import BaseTestCase


class MonitoringTestCase(BaseTestCase):

    def test_disable(self):
        # Setup a monitoring
        monitoring_json, expected_config = self.setup_monitoring_1()

        # Run the create action on the monitoring
        monitoring_1_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup another monitoring with the same host but different services
        # and email
        monitoring_json, expected_config = self.setup_monitoring_2()

        # Run the create action on the second monitoring
        monitoring_2_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup a monitoring for the second that disables it
        monitoring_json, expected_config = self.setup_monitoring_3()

        # Run the update action on the second monitoring to disable it
        monitoring_2_id = self.run_action(
            'update', monitoring_json, expected_config, monitoring_2_id)

        # Setup a monitoring for the first that disables it
        monitoring_json, expected_config = self.setup_monitoring_4()

        # Run the update action on the first monitoring to disable it
        monitoring_1_id = self.run_action(
            'update', monitoring_json, expected_config, monitoring_1_id)

    def setup_monitoring_1(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 1,
                "checks": {
                    "ssh": 1,
                    "http": 0,
                    "https": 0,
                    "smtp": 0,
                    "hddUsage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpuLoad": 0
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

define service {
    use                     generic-service
    host_name               google.com
    service_description     ssh
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_ssh
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

    def setup_monitoring_2(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 1,
                "checks": {
                    "ssh": 0,
                    "http": 1,
                    "https": 0,
                    "smtp": 0,
                    "hddUsage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpuLoad": 0
                },
                "token": '1'
            },
            "contact": {
                "username": 'user1',
                "alias": 'someotheruser',
                "email": 'someothermail@somedomain.org',
                "token": '2'
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
    contact_groups          user1-somemail@somedomain.org_GROUP,user1-someothermail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  1
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     ssh
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_ssh
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     http
    contact_groups          user1-someothermail@somedomain.org_GROUP
    check_command           check_http
}

define contact {
    contact_name                    user1-someothermail@somedomain.org
    use                             generic-contact
    alias                           someotheruser
    email                           someothermail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          2
}

define contactgroup {
    contactgroup_name       user1-someothermail@somedomain.org_GROUP
    alias                   user1-someothermail@somedomain.org_GROUP
    members                 user1-someothermail@somedomain.org
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")

    def setup_monitoring_3(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 0,
                "checks": {
                    "ssh": 0,
                    "http": 1,
                    "https": 0,
                    "smtp": 0,
                    "hddUsage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpuLoad": 0
                },
                "token": '1'
            },
            "contact": {
                "username": 'user1',
                "alias": 'someotheruser',
                "email": 'someothermail@somedomain.org',
                "token": '2'
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

define service {
    use                     generic-service
    host_name               google.com
    service_description     ssh
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_ssh
}

define contact {
    contact_name                    user1-someothermail@somedomain.org
    use                             generic-contact
    alias                           someotheruser
    email                           someothermail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          2
}

define contactgroup {
    contactgroup_name       user1-someothermail@somedomain.org_GROUP
    alias                   user1-someothermail@somedomain.org_GROUP
    members                 user1-someothermail@somedomain.org
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")

    def setup_monitoring_4(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 0,
                "checks": {
                    "ssh": 1,
                    "http": 0,
                    "https": 0,
                    "smtp": 0,
                    "hddUsage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpuLoad": 0
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

        config = '''define contact {
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
