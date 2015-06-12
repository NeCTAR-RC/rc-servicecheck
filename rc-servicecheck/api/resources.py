import json
import os
import subprocess
import socket

from django.conf.urls import url
from django.contrib.auth.models import User
from django.db import models
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.models import create_api_key
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from nectar_monitor_rest import settings
from rest.models import Contact, Host, Monitoring
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from tastypie.exceptions import BadRequest
from tastypie import http
import uuid
from django.core.mail.message import EmailMessage


# Generates an api_key whe new user is created
models.signals.post_save.connect(create_api_key, sender=User)

# Serialise to JSON format
json_serializer = Serializer(formats=['json'])


class MonitoringResource(ModelResource):
    """
    A subclass of ``ModelResource`` that provides CRUD operations on a
    monitoring model while maintaining the state of the hosts and services
    under monitoring with Nagios.
    """
    class Meta:
        object_class = Monitoring
        queryset = Monitoring.objects.all()
        resource_name = 'monitoring'
        serializer = json_serializer
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        allowed_method = ['get', 'post', 'put', 'delete']
        filtering = {
            'id': ['exact']
        }
        always_return_data = True
        max_limit = None

    STATE_OK = 0
    STATE_WARNING = 1
    STATE_CRITICAL = 2
    STATE_UNKNOWN = 3

    STATE_UP = 0
    STATE_DOWN = 1

    HAS_NOT_BEEN_CHECKED = 0
    HAS_BEEN_CHECKED = 1

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<id>\d+)/$" %
                self._meta.resource_name, self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/unsubscribe/$" %
                self._meta.resource_name, self.wrap_view('unsubscribe'),
                name="unsubscribe"),
        ]

    def get_object_list(self, request):
        """
        Returns a list of monitoring objects in JSON format.

        The list is filtered by a given tenant_id.
        """
        # if passing tenantID
        try:
            tenant_id = request.GET['tenant_id']
            return (super(MonitoringResource, self).get_object_list(request).
                    filter(contact__username=tenant_id))
        except:
            raise Http404

    def alter_list_data_to_serialize(self, request, data):
        """
        Adds extra detail data to the list of monitorings before they get
        serialised and returned to the user.
        """
        # Add extra fields to the returned data
        for d in data["objects"]:
            d.data['host'] = {'ip': d.obj.host.host_ip}
            d.data['contact'] = {'username': d.obj.contact.username,
                                 'email': d.obj.contact.email}

            status = self.query_host_status(d.obj.host.host_ip, {})
            status = self.query_services_status(d.obj.host.host_ip,
                                                d.obj.contact.name(),
                                                status)

            d.data['status'] = status

        return data

    def alter_detail_data_to_serialize(self, request, data):
        """
        Adds extra detail data to the monitoring before it gets
        serialised and returned to the user.
        """
        # Add extra fields to the returned data
        data.data['host'] = {'ip': data.obj.host.host_ip}
        data.data['contact'] = {'username': data.obj.contact.username,
                                'email': data.obj.contact.email}

        status = self.query_host_status(data.obj.host.host_ip, {})
        status = self.query_services_status(data.obj.host.host_ip,
                                            data.obj.contact.name(),
                                            status)

        data.data['status'] = status

        return data

    def query_nagios(self, command, output_format='json'):
        """
        Executes a query on Nagios using the available socket and returns the
        results.

        Query results can be returned in a specified output format.
        """
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(settings.LIVESTATUS_SOCKET_PATH)
        s.send(command)
        s.shutdown(socket.SHUT_WR)

        result = s.recv(100000000)

        if output_format == 'json':
            return json.loads(result)
        elif output_format == 'csv':
            return [line.split(';') for line in result.split('\n')[:-1]]
        else:
            return result

    def query_host_status(self, host_ip, status={}):
        """
        Executes a query on Nagios to return the current soft state of a host.
        """
        # Get the state of the specified host
        command_host = '''GET hosts
Columns: host_state has_been_checked
Filter: host_name = HOST_NAME
OutputFormat: json
Limit: 1
'''
        command_host = command_host.replace('HOST_NAME', host_ip)

        result_host = self.query_nagios(command_host)

        # The result will be an array with just an integer value
        # Format it into the same format as the services are return in,
        # by including that it was ping check
        if(len(result_host) > 0):
            # Host state is UP or DOWN so convert DOWN (1) into CRITICAL (2)
            if result_host[0][0] == self.STATE_DOWN:
                status["ping"] = self.STATE_CRITICAL
            else:
                # There is no pending state so we use 'has_been_checked' to
                # find out if it is pending
                if result_host[0][1] == self.HAS_NOT_BEEN_CHECKED:
                    # Set status to UNKNOWN when host hasn't been checked
                    status["ping"] = self.STATE_UNKNOWN
                else:
                    status["ping"] = result_host[0][0]

        return status

    def query_services_status(self, host_ip, contact_name, status={}):
        """
        Executes a query on Nagios to return the current soft state of all the
        services for a contact on a given host.
        """
        # Get the last hard state on all the services for the given host and
        # contact
        command_services = '''GET services
Columns: description service_state has_been_checked
Filter: host_name = HOST_NAME
Filter: contacts >= CONTACT_NAME
OutputFormat: json
'''
        command_services = command_services.replace('HOST_NAME', host_ip)
        command_services = command_services.replace('CONTACT_NAME',
                                                    contact_name)

        results = self.query_nagios(command_services)

        # Format the services in service: value pairs
        for result in results:
            # There is no pending state so we use 'has_been_checked' to find
            # out if it is pending
            if result[2] == self.HAS_NOT_BEEN_CHECKED:
                # Set status to UNKNOWN when service hasn't been checked
                status[result[0]] = self.STATE_UNKNOWN
            else:
                status[result[0]] = result[1]

        return status

    def obj_create(self, bundle, **kwargs):
        """
        Creates a new monitoring using the given host and contact data.

        The Nagios configuration is updated and restarted with the new
        monitoring.
        """
        # Get an existing host by IP or create a new one
        try:
            host = Host.objects.get(host_ip=bundle.data['host']['ip'])
        except ObjectDoesNotExist:
            host = Host()
            host.host_ip = bundle.data['host']['ip']
            host.token = self.generate_host_token()
            host.save()

        # Get an existing user by username/email or create a new one
        try:
            contact = (Contact.objects.
                       get(username=bundle.data['contact']['username'],
                           email=bundle.data['contact']['email']))
        except (KeyError, ObjectDoesNotExist):
            contact = Contact()
            contact.username = bundle.data['contact']['username']
            contact.alias = bundle.data['contact']['alias']
            contact.email = bundle.data['contact']['email']
            contact.token = self.generate_contact_token()
            contact.save()

        # Prevent creating a new monitoring when one exists
        if Monitoring.objects.filter(host=host, contact=contact).exists():
            raise BadRequest('Monitoring already exists for ' + host.host_ip +
                             ' and ' + contact.name())

        # Save the service
        monitoring = self.save_monitoring(host, contact, bundle.data)

        # Write the host and contact configurations
        self.write_host_configuration(host)
        self.write_contact_configuration(contact)

        self.restart_nagios()

        # Return the monitoring. Will be rendered as JSON
        bundle.obj = monitoring

        return bundle

    def obj_update(self, bundle, **kwargs):
        """
        Updates an existing monitoring using the given host and contact data.

        The Nagios configuration is updated and restarted with the new
        monitoring.
        """
        # Get the monitoring by id
        try:
            monitoring = Monitoring.objects.get(id=kwargs['id'])
        except (KeyError, ObjectDoesNotExist):
            raise Http404

        host = monitoring.host
        contact = monitoring.contact

        # Keep a reference to the previous host/contact as the monitoring may
        # reference an other one
        previous_host = monitoring.host
        previous_contact = monitoring.contact

        # Check if the host IP has changed
        if host.host_ip != bundle.data['host']['ip']:
            # Assign an existing/new host with the new host IP
            try:
                host = Host.objects.get(host_ip=bundle.data['host']['ip'])
            except ObjectDoesNotExist:
                host = Host()
                host.host_ip = bundle.data['host']['ip']
                host.token = self.generate_host_token()
                host.save()

        # Check if the contact has changed
        if (contact.username != bundle.data['contact']['username'] or
                contact.email != bundle.data['contact']['email']):
            # Assign an existing/new contact with the new username
            try:
                contact = (Contact.objects.
                           get(username=bundle.data['contact']['username'],
                               email=bundle.data['contact']['email']))
            except ObjectDoesNotExist:
                contact = Contact()
                contact.username = bundle.data['contact']['username']
                contact.alias = bundle.data['contact']['alias']
                contact.email = bundle.data['contact']['email']
                contact.token = self.generate_contact_token()
                contact.save()

        # Prevent creating a new monitoring when one exists,
        # but only if the host or contact has changed, otherwise,
        # this will return a false positive as it will check itself
        if host != previous_host or contact != previous_contact:
            if Monitoring.objects.filter(host=host, contact=contact).exists():
                raise BadRequest('Monitoring already exists for ' +
                                 host.host_ip + ' and ' + contact.alias)

        # Save the new host to the monitoring
        monitoring.host = host
        monitoring.contact = contact
        monitoring.save()

        # Update the contact alias
        contact.alias = bundle.data['contact']['alias']
        contact.save()

        # Save the monitoring
        monitoring = self.save_monitoring(host, contact, bundle.data)

        # Write the host and contact configurations
        self.write_host_configuration(host)
        self.write_contact_configuration(contact)

        # Also update the previous host's configuration if the host was changed
        if host.id != previous_host.id:
            self.write_host_configuration(previous_host)

        # Also update the previous contact's configuration if the contact was
        # changed
        if contact.id != previous_contact.id:
            self.write_contact_configuration(previous_contact)

        self.restart_nagios()

        # Return the monitoring. Will be rendered as JSON
        bundle.obj = monitoring

        return bundle

    def obj_delete(self, bundle, **kwargs):
        """
        Deletes an existing monitoring.

        The Nagios configuration is updated and restarted with the new
        monitoring.
        """
        # Get the monitoring by id
        try:
            monitoring = Monitoring.objects.get(id=kwargs['id'])
        except ObjectDoesNotExist:
            raise Http404

        # Keep references as the configuration will be updated after the
        # monitoring is deleted
        host = monitoring.host
        contact = monitoring.contact

        # Delete the monitoring
        monitoring.delete()

        # Write the host and contact configurations
        self.write_host_configuration(host)
        self.write_contact_configuration(contact)

        self.restart_nagios()

    def save_monitoring(self, host, contact, data):
        """
        Persists a new or existing monitoring using the host, contact and other
        data provided.

        The persisted monitoring is returned.
        """
        # Get an existing monitoring or add a new monitoring
        try:
            monitoring = Monitoring.objects.get(host=host, contact=contact)
        except ObjectDoesNotExist:
            monitoring = Monitoring()
            monitoring.host = host
            monitoring.contact = contact

            monitoring.creator_name = data['creator']['name']
            monitoring.creator_email = data['creator']['email']

        # Set whether the monitoring is enabled
        if data['host']['enabled']:
            monitoring.enabled = True
        else:
            monitoring.enabled = False

        # Set which monitoring services the contact has assigned for the host
        monitoring.name = data['host']['name']
        monitoring.ssh = data['host']['checks']['ssh']
        monitoring.http = data['host']['checks']['http']
        monitoring.https = data['host']['checks']['https']
        monitoring.smtp = data['host']['checks']['smtp']
        monitoring.hdd_usage = data['host']['checks']['hdd_usage']
        monitoring.mysql = data['host']['checks']['mysql']
        monitoring.postgres = data['host']['checks']['postgres']
        monitoring.cpu_load = data['host']['checks']['cpu_load']
        monitoring.save()

        return monitoring

    def unsubscribe(self, request, **kwargs):
        """
        A request method that attempts to unsubscribe a contact's email from a
        monitoring.

        This method is just a proxy to another method that will perform the
        unsubscribing. It allows the other method to be easily mocked for
        testing.
        """
        return self._unsubscribe(request.GET.get('host_token'),
                                 request.GET.get('contact_token'))

    def _unsubscribe(self, host_token, contact_token):
        """
        Unsubscribe a contact's email from a monitoring.

        The Nagios configuration is updated and restarted with the changes.
        """
        try:
            monitoring = Monitoring.objects.get(host__token=host_token,
                                                contact__token=contact_token)
        except (KeyError, ObjectDoesNotExist):
            raise Http404

        if monitoring.host.token != host_token:
            return http.HttpUnauthorized

        # Token must match the monitoring's contact token
        if monitoring.contact.token != contact_token:
            return http.HttpUnauthorized()

        # Keep track of the contact prior to it being removed
        previous_contact = monitoring.contact

        # Get an existing contact by username with no email or create a new
        # contact with the same username but no email
        try:
            contact = Contact.objects.get(username=previous_contact.username,
                                          email=None)
        except (KeyError, ObjectDoesNotExist):
            contact = Contact()
            contact.username = previous_contact.username
            contact.alias = previous_contact.alias
            contact.email = None
            contact.token = self.generate_contact_token()
            contact.save()

        # Assign the new contact with no email
        monitoring.contact = contact

        # Disable the monitoring
        monitoring.enabled = False
        monitoring.save()

        # Update the host config to remove the previous contact
        self.write_host_configuration(monitoring.host)

        # Update the previous contact as it may need to be deleted if not
        # required anymore
        self.write_contact_configuration(previous_contact)

        self.restart_nagios()

        self.send_unsubscribe_email(monitoring.host.host_ip,
                                    previous_contact.email,
                                    monitoring.creator_email)

        return http.HttpResponse("Successfully unsubscribed " +
                                 previous_contact.email + " from monitoring " +
                                 monitoring.host.host_ip)

    def send_unsubscribe_email(self, host_ip, unsubscribed_email, creator_email):
        """
        Sends an email to the unsubscribed contact and creator of a monitoring.

        The email notifies that the contact's email of the monitoring has been
        removed.
        """
        # Subject header
        subject = ('[NeCTAR Monitoring] ' + unsubscribed_email +
                   ' has been unsubscribed from ' + host_ip)

        # Email body content
        body = (unsubscribed_email + ' has been unsubscribed from the ' +
                host_ip + ' monitoring alerts. There is no email subscribed ' +
                'to receive monitoring alerts, monitoring to ' + host_ip +
                ' has been disabled.')

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.UNSUBSCRIBE_EMAIL_FROM,
            to=[unsubscribed_email],
            cc=[creator_email]
        )

        email.content_subtype = "text"
        email.send()

    def write_host_configuration(self, host):
        """
        Generates the host configuration file for an enabled host. The file
        contains the host and service Nagios definitions.

        If no enabled monitorings are assigned to the host, any previous
        configurations for the host are deleted.

        If no monitorings are assigned to the host, the host model is deleted.
        """
        # Generate the host config for all enabled monitorings for the host
        content = self.generate_host(host,
                                     Monitoring.objects.filter(host=host,
                                                               enabled=True))

        if not content:
            try:
                # Delete the host config if no contact monitoring services are
                # assigned to the host
                os.remove(self.get_host_filename(host.id))
            except OSError:
                pass

            # Delete the host if no enabled and disabled monitorings are
            # associated to it
            if not Monitoring.objects.filter(host=host).exists():
                host.delete()
        else:
            # Otherwise write to the host config
            with open(self.get_host_filename(host.id), 'w') as f:
                # Add enabled monitoring services to the host config if any of
                # the contacts have assigned it
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         ssh=True,
                                                         enabled=True)),
                                                 'ssh', 'check_ssh')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         http=True,
                                                         enabled=True)),
                                                 'http', 'check_http')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         https=True,
                                                         enabled=True)),
                                                 'https',
                                                 'check_https_cert!31')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         smtp=True,
                                                         enabled=True)),
                                                 'smtp', 'check_smtp')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         hdd_usage=True,
                                                         enabled=True)),
                                                 'disk',
                                                 'check_nrpe_1arg!' +
                                                 'check_all_disks')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         mysql=True,
                                                         enabled=True)),
                                                 'mysql',
                                                 'check_nrpe_1arg!' +
                                                 'check_mysql')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         postgres=True,
                                                         enabled=True)),
                                                 'postgres',
                                                 'check_nrpe_1arg!' +
                                                 'check_pgsql')
                content += self.generate_service(host,
                                                 (Monitoring.objects.
                                                  filter(host=host,
                                                         cpu_load=True,
                                                         enabled=True)),
                                                 'serverload',
                                                 'check_nrpe_1arg!' +
                                                 'check_load')

                f.write(content)

    def write_contact_configuration(self, contact):
        """
        Generates the contact configuration file for a contact. The file
        contains the contact and contact group Nagios definitions.

        If no monitorings are assigned to the contact, the contact model is
        deleted and any previous configurations for the contact are deleted.
        """
        # Don't write the config if the contact has no associated monitorings
        if not Monitoring.objects.filter(contact=contact).exists():
            try:
                # Delete any existing contact config
                os.remove(self.get_contact_filename(contact.id))
            except OSError:
                pass

            # Delete the contact
            contact.delete()
        else:
            # Generate the contact config
            content = self.generate_contact(contact)

            # Write the contact config
            with open(self.get_contact_filename(contact.id), 'w') as f:
                f.write(content)

    def restart_nagios(self):
        """
        Attempts to restart the Nagios server if there are no Nagios
        configuration errors.
        """
        # Check if the configurations are valid.
        res = subprocess.call(['sudo', 'service', 'nagios', 'checkconfig'])

        if res != 0:
            raise Exception("Configuration error.")

        # Restart nagios.
        res = subprocess.call(['sudo', 'systemctl', 'restart', 'nagios'])

        if res != 0:
            raise Exception("Nagios restart error.")

    def generate_host(self, host, monitorings):
        """
        Generates a host configuration definition.

        The definition is returned as a string.
        """
        # Only generate the host if contacts have assigned monitorings to the
        # host
        if len(monitorings) == 0:
            return False

        # Append each contact's group name to the host's contact groups
        contact_groups = ''
        for monitoring in monitorings:
            contact_groups += monitoring.contact.group_name() + ','

        # Remove the trailing comma
        contact_groups = contact_groups.rstrip(',')

        data = '''define host {
    use                     linux-server
    host_name               %s
    alias                   %s
    contact_groups          %s
    check_command           check_ping!500.0,20%%!1500.0,60%%
    _token                  %s
}

''' % (host.host_ip, host.host_ip, contact_groups, host.token)

        return data

    def generate_service(self, host, monitorings, description, command):
        """
        Generates a service configuration definition.

        The definition is returned as a string.
        """
        # Only generate the service if contacts have assigned the monitorings
        # to the host
        if len(monitorings) == 0:
            return ''

        # Append each contact's group name to the service's contact groups
        contact_groups = ''
        for monitoring in monitorings:
            contact_groups += monitoring.contact.group_name() + ','

        # Remove the trailing comma
        contact_groups = contact_groups.rstrip(',')

        data = '''define service {
    use                     generic-service
    host_name               %s
    service_description     %s
    contact_groups          %s
    check_command           %s
}

''' % (host.host_ip, description, contact_groups, command)

        return data

    def generate_contact(self, contact):
        """
        Generates contact and contact group configuration definitions.

        The definitions are returned as a string.
        """
        data = '''define contact {
    contact_name                    %s
    use                             generic-contact
    alias                           %s
    email                           %s
    service_notification_commands   notify-service-by-email
    host_notification_commands      notify-host-by-email
    _token                          %s
}

define contactgroup {
    contactgroup_name       %s
    alias                   %s
    members                 %s
}

''' % (contact.name(), contact.alias, contact.email, contact.token,
      contact.group_name(), contact.group_name(), contact.name())

        return data

    def get_host_filename(self, host_id):
        """
        Returns an absolute filename path for a given host.
        """
        return settings.TEMP_PATH + 'host-' + str(host_id) + '.cfg'

    def get_contact_filename(self, contact_id):
        """
        Returns an absolute filename path for a given contact.
        """
        return settings.TEMP_PATH + 'contact-' + str(contact_id) + '.cfg'

    def generate_host_token(self):
        """
        Returns a randomly generated token string.
        """
        return uuid.uuid1().hex

    def generate_contact_token(self):
        """
        Returns a randomly generated token string.
        """
        return uuid.uuid1().hex
