from test.common import BaseTestCase


class MonitoringTestCase(BaseTestCase):

    def test_services_with_different_contacts(self):
        # Setup a monitoring
        monitoring_json, expected_config = self.setup_monitoring_1()

        # Run the create action on the monitoring
        self.run_action(
            'create', monitoring_json, expected_config)

        # Setup another monitoring with the same host but different services
        # and contact
        monitoring_json, expected_config = self.setup_monitoring_2()

        # Run the create action on the second monitoring
        monitoring_2_id = self.run_action(
            'create', monitoring_json, expected_config)

        # Setup another monitoring that removes https from monitoring number 2
        monitoring_json, expected_config = self.setup_monitoring_3()

        # Run the update action on monitoring 2
        monitoring_2_id = self.run_action(
            'update', monitoring_json, expected_config, monitoring_2_id)

        # Setup a config that deletes monitoring 2
        monitoring_json, expected_config = self.setup_monitoring_4()

        # Run the delete action on monitoring 2
        self.run_action(
            'delete', monitoring_json, expected_config, monitoring_2_id)

    def setup_monitoring_1(self):
        data = {
            "host": {
                "ip": 'google.com',
                "name": 'google',
                "enabled": 1,
                "checks": {
                    "ssh": 1,
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

define service {
    use                     generic-service
    host_name               google.com
    service_description     http
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_http
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
                    "ssh": 1,
                    "http": 0,
                    "https": 1,
                    "smtp": 0,
                    "hddUsage": 0,
                    "mysql": 0,
                    "postgres": 0,
                    "cpuLoad": 0
                },
                "token": '1'
            },
            "contact": {
                "username": 'user2',
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
    contact_groups          user1-somemail@somedomain.org_GROUP,user2-someothermail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  1
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     ssh
    contact_groups          user1-somemail@somedomain.org_GROUP,user2-someothermail@somedomain.org_GROUP
    check_command           check_ssh
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     http
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_http
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     https
    contact_groups          user2-someothermail@somedomain.org_GROUP
    check_command           check_https_cert!31
}

define contact {
    contact_name                    user2-someothermail@somedomain.org
    use                             generic-contact
    alias                           someotheruser
    email                           someothermail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          2
}

define contactgroup {
    contactgroup_name       user2-someothermail@somedomain.org_GROUP
    alias                   user2-someothermail@somedomain.org_GROUP
    members                 user2-someothermail@somedomain.org
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
                "username": 'user2',
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
    contact_groups          user1-somemail@somedomain.org_GROUP,user2-someothermail@somedomain.org_GROUP
    check_command           check_ping!500.0,20%!1500.0,60%
    _token                  1
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     ssh
    contact_groups          user1-somemail@somedomain.org_GROUP,user2-someothermail@somedomain.org_GROUP
    check_command           check_ssh
}

define service {
    use                     generic-service
    host_name               google.com
    service_description     http
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_http
}

define contact {
    contact_name                    user2-someothermail@somedomain.org
    use                             generic-contact
    alias                           someotheruser
    email                           someothermail@somedomain.org
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          2
}

define contactgroup {
    contactgroup_name       user2-someothermail@somedomain.org_GROUP
    alias                   user2-someothermail@somedomain.org_GROUP
    members                 user2-someothermail@somedomain.org
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")

    def setup_monitoring_4(self):
        data = {
            "host": {
                "token": '1'
            },
            "contact": {
                "token": '1'
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

define service {
    use                     generic-service
    host_name               google.com
    service_description     http
    contact_groups          user1-somemail@somedomain.org_GROUP
    check_command           check_http
}

'''

        # Return the json data and a string representation of the config
        # (newlines written as \n)
        return data, repr(config).strip("'")
