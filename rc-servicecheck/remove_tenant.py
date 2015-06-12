import os
import sys
from optparse import OptionParser

sys.path.append(os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = 'nectar_monitor_rest.settings'

from api.resources import MonitoringResource
from rest.models import Monitoring


def main():
    parser = OptionParser()
    parser.add_option(
        "-t", dest="tenant_id", help="Tenancy/Project unique identifier")
    options, args = parser.parse_args()

    if options.tenant_id:
        tenant_id = options.tenant_id

        # reusing the write_host_conf, write_contact_conf and
        # restart_nagios functions from the monitoring resource
        mr = MonitoringResource()

        # Get all monitoring associated with tenancy
        mon_list = Monitoring.objects.filter(contact__username=tenant_id)

        if mon_list:
            for mon in mon_list:
                print("Removing monitoring checks for: " + mon.host.host_ip)
                # Keep references as the configuration will be
                # updated after the monitoring is deleted
                host = mon.host
                contact = mon.contact

                # Delete the monitoring
                mon.delete()

                # Write the host and contact configurations
                mr.write_host_configuration(host)
                mr.write_contact_configuration(contact)

            print("Restarting Nagios...")
            mr.restart_nagios()
            print(
                "Success! Tenancy monitoring checks removed for " + tenant_id)

        else:
            print("No monitoring checks found for tenancy: " + tenant_id)

    else:
        print("Enter a tenant_id(-t <tenant_id>) or see -h for help")


if __name__ == "__main__":
    main()
