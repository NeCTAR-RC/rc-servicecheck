import os
import sys
from optparse import OptionParser

sys.path.append(os.getcwd())
from nectar_monitor_rest import settings
os.environ["DJANGO_SETTINGS_MODULE"] = 'nectar_monitor_rest.settings'

from api.resources import MonitoringResource
from rest.models import Monitoring


def main():
    """
    Restores the host and contact configuration files for all
    enabled monitorings
    """
    parser = OptionParser()
    parser.add_option("-v", dest="verbose", nargs=0,
                      help="Print output to display")
    options, args = parser.parse_args()

    # Delete existing configuration files if required
    if raw_input("Delete all existing configurations in " +
                 settings.TEMP_PATH + "? [y/N]: ") == "y":
        for f in os.listdir(settings.TEMP_PATH):
            # Only delete host and contact files
            if str(f).startswith("host") or str(f).startswith("contact"):
                filepath = os.path.join(settings.TEMP_PATH, f)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                        if options.verbose is not None:
                            print "Deleted " + filepath
                except Exception as e:
                    print e

    mr = MonitoringResource()

    # Get only enabled monitorings
    monitorings = Monitoring.objects.filter(enabled=True)

    if monitorings:
        print "Restoring " + str(len(monitorings)) + " monitorings..."
        for monitoring in monitorings:
            # Write the host configurations
            if options.verbose is not None:
                print ("Writing host configuration for Monitoring (" +
                       str(monitoring.pk) + ") on " + str(monitoring.host))
            mr.write_host_configuration(monitoring.host)

            # Write the contact configurations
            if options.verbose is not None:
                print ("Writing contact configuration for Monitoring (" +
                       str(monitoring.pk) + ") on " + str(monitoring.contact))
            mr.write_contact_configuration(monitoring.contact)

        print "Restarting Nagios..."
        mr.restart_nagios()

        print "Success!!!"


if __name__ == "__main__":
    main()
