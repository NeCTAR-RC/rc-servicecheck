from django.test import TestCase
from mock import patch, mock_open
from tastypie.bundle import Bundle

from api.resources import MonitoringResource


class BaseTestCase(TestCase):

    def run_action(self, action, monitoring_json, expected_config,
                   monitoring_id=None):
            bundle = Bundle(data=monitoring_json)

            with patch('__builtin__.open', mock_open(),
                       create=True) as mock_open_method:
                with patch('os.remove', return_value=None):
                    with patch('api.resources.MonitoringResource.' +
                               'generate_host_token',
                               return_value=bundle.data['host']['token']):
                        with patch('api.resources.MonitoringResource.' +
                                   'generate_contact_token',
                                   return_value=(bundle.data['contact']
                                                 ['token'])):
                            with patch('api.resources.MonitoringResource.' +
                                       'restart_nagios', return_value=None):
                                with patch('api.resources.' +
                                           'MonitoringResource.' +
                                           'send_unsubscribe_email',
                                           return_value=None):
                                    monitoringResource = MonitoringResource()

                                    if action == 'create':
                                        bundle = (monitoringResource.
                                                  obj_create(bundle))
                                    elif action == 'update':
                                        bundle = (monitoringResource.
                                                  obj_update(bundle,
                                                             id=monitoring_id))
                                    elif action == 'delete':
                                        bundle = (monitoringResource.
                                                  obj_delete(bundle,
                                                             id=monitoring_id))
                                    elif action == 'unsubscribe':
                                        (monitoringResource.
                                         _unsubscribe((bundle.
                                                       data['host']['token']),
                                                      (bundle.data
                                                       ['contact']['token'])))
                                    else:
                                        raise Exception('Unsupported ' +
                                                        'monitoring action')

                                    # Get the contents that was going to be
                                    # written to the configuration files
                                    writes = filter(lambda x:
                                                    'write' in str(x),
                                                    (mock_open_method.
                                                     mock_calls))

                                    actual_config = ''

                                    for write in writes:
                                        config = str(write)

                                        # Get only the string that wqs passed
                                        # into the write() method
                                        config = (config[len('call().write(u'):
                                                         ].strip("')"))

                                        actual_config += config

                                    # Check that the configurations
                                    # are the same
                                    self.assertEqual(actual_config,
                                                     expected_config)

            # Return back the id of the monitoring
            if action is not 'delete' and action is not 'unsubscribe':
                return bundle.obj.id
