from test.common import BaseTestCase


class MonitoringTestCase(BaseTestCase):

    def test_unsubscribe(self):
        # Setup a monitoring
        monitoring_json, expected_config = self.setup_monitoring_1()

        # Run the create action on the monitoring
        monitoring_1_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup a second monitoring with the same host but different contact
        monitoring_json, expected_config = self.setup_monitoring_2()

        # Run the create action on the second monitoring
        monitoring_2_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup a third monitoring with a different host but same contact as
        # the first
        monitoring_json, expected_config = self.setup_monitoring_3()

        # Run the create action on the third monitoring
        monitoring_3_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup a monitoring to validate the unsubscribing of the second
        # monitoring
        monitoring_json, expected_config = self.setup_monitoring_4()

        # Run the unsubscribe action on the second monitoring
        self.run_action(
            'unsubscribe', monitoring_json, expected_config, monitoring_2_id)

        # Setup a monitoring to validate the unsubscribing of the third
        # monitoring
        monitoring_json, expected_config = self.setup_monitoring_5()

        # Run the unsubscribe action on the third monitoring
        self.run_action(
            'unsubscribe', monitoring_json, expected_config, monitoring_3_id)

        # Setup the second monitoring again
        monitoring_json, expected_config = self.setup_monitoring_2()

        # Run the update action on the second monitoring
        monitoring_2_id = self.run_action(
            'update', monitoring_json, expected_config, monitoring_2_id)

        # Setup a monitoring to validate the unsubscribing of the second
        # monitoring again
        monitoring_json, expected_config = self.setup_monitoring_4()

        # Run the unsubscribe action on the second monitoring
        self.run_action(
            'unsubscribe', monitoring_json, expected_config, monitoring_2_id)

        # Setup a monitoring to validate the unsubscribing of the first and
        # final monitoring
        monitoring_json, expected_config = self.setup_monitoring_6()

        # Run the unsubscribe action on the first and last remaining monitoring
        self.run_action(
            'unsubscribe', monitoring_json, expected_config, monitoring_1_id)

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

    def setup_monitoring_2(self):
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
                "username": 'user2',
                "alias": 'someuser',
                "email": 'somemail@somedomain.org',
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
    contact_groups          user1-somemail@somedomain.org_GROUP,user2-somemail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  1
}

define contact {
    contact_name                    user2-somemail@somedomain.org
    use                             generic-contact
    alias                           someuser
    email                           somemail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          2
}

define contactgroup {
    contactgroup_name       user2-somemail@somedomain.org_GROUP
    alias                   user2-somemail@somedomain.org_GROUP
    members                 user2-somemail@somedomain.org
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")

    def setup_monitoring_3(self):
        data = {
            "host": {
                "ip": 'theage.com',
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
                "token": '3'
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
    host_name               theage.com
    alias                   theage.com
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  3
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

    # TODO: need to return host->token
    def setup_monitoring_4(self):
        data = {
            "host": {
                "token": '1'
            },
            "contact": {
                "token": '2'
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

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")

    def setup_monitoring_5(self):
        data = {
            "host": {
                "token": '3'
            },
            "contact": {
                "token": '1'
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

    def setup_monitoring_6(self):
        data = {
            "host": {
                "token": '1'
            },
            "contact": {
                "token": '1'
            }
        }

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, ''
