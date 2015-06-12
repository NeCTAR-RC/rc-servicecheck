Montioring Project quick setup guide (Incl rcportal + nagios + rest server)

Setting up rcportal
-------------------
The monitoring component will talk to a restful api to configure the nagios checks. The monitoring component does not require a database as all data is stored on the nagios server.

Setup the rcportal. Follow instructions found in project readme.
Additional monitoring setup
In the "settings.py" set the “NAGIOS” values:
NAGIOS_URL = the restful api url (http://<hostname>/rest/api/v1/monitoring/)
NAGIOS_USER = rest auth user
NAGIOS_KEY = rest api key

The nagios user and key will be generated on nagios rest server, explained in the “Nagios Rest Server” section.


Nagios Server
-------------
Simple Fault Tolerant Nagios Cluster:
https://bashinglinux.wordpress.com/2013/06/01/fault-tolerant-nagios-cluster/

After spinning up a basic heat template. This was based on Centos 7.

echo n2.v3apps.org.au > /etc/hostname
hostname n2.v3apps.org.au

mkdir /etc/ssl/certs/n2.v3apps.org.au
Copy key and cert there.

chmod 600 hostkey.pem
restorecon -Rv /etc/ssl/certs/n2.v3apps.org.au

Add cert and key to: vim /etc/httpd/conf.d/ssl.conf
	SSLCertificateFile /etc/ssl/certs/n2.v3apps.org.au/hostcert.pem
	SSLCertificateKeyFile /etc/ssl/certs/n2.v3apps.org.au/hostkey.pem

Uncomment line 42 "SSLRequireSSL": vim /etc/httpd/conf.d/nagios.conf

Add: /etc/nagios/conf.d/custom.cfg
define command {
   command_name check_https_cert
   command_line /usr/lib64/nagios/plugins/check_http -S -I $HOSTADDRESS$ -C $ARG1$
}

Change: /etc/nagios/objects/localhost.cfg
  check_command        check_https_cert!31

On n2, edit: vim /etc/nagios/private/resource.cfg
$USER2$="nrpe -H n1.v3apps.org.au -c check_nag"

Then edit (as per Fault Tolerant Nagios Cluster guide): vim /etc/nagios/objects/commands.cfg
  command_line   eval $USER2$ || ............<rest of check>

sed -i s/allowed_hosts=127.0.0.1/allowed_hosts=127.0.0.1,::1,n1.v3apps.org.au/ /etc/nagios/nrpe.cfg
systemctl restart nrpe

Install the check_nag script and: restorecon -Rv /usr/lib64/nagios/plugins/check_nag

Add to /etc/nagios/nagios.cfg (on both servers): cfg_dir=/etc/nagios/nectar
mkdir /etc/nagios/nectar
chown :nagios /etc/nagios/nectar
chmod 750 /etc/nagios/nectar

Add: /etc/cron.hourly/nagios-sync


Here's the nagios-sync cron job:
#!/bin/bash

count=$(/usr/bin/ping -W2 -c1 n2.v3apps.org.au | grep icmp | wc -l )

if [ $count -eq 1 ]; then
  /usr/bin/rsync --delete -a /etc/nagios/nectar n2.v3apps.org.au:/etc/nagios/
  /usr/bin/ssh n2.v3apps.org.au 'service nagios checkconfig && systemctl restart nagios'
fi


Nagios Rest Server
------------------
Requirements
debian or centos equivalent distro
Apache 2
mod_wsgi
python 2.7
django 1.6
django-tastypie 0.12
mysql (or any dbms compatible with django)

The restful api is a django application that uses the tastypie api for the restful functionality. The rest server must be deployed on the same server as N1. The monitoring module of the rcportal will interact with the nagios server by making restful calls to the rest service which will then write to nagios configuration files and restart the nagios service.
Get the project source code
git clone <monitoring-rest>

Run tox to create the virtualenv with all the python dependencies.

To activate run” “source <app directory>./tox/py27/bin/activate”
Setting up the django application database
Set the database configuration in the “nectar_monitoring_rest/settings.py"

Setup the database using: “python manage.py syncdb”
Follow the prompts to create a super user.
Create an api key for the rest authentication
Run the django admin and log in as super user
http://<hostname>/rest/admin/

In the django admin create a new user that will be used for rest authentication. After creating the user go to the "api keys” under “Tastypie”, here you will find a "api key” generated for the user created. Note the “username" and "api key” as these values will need to be set in the “settings.py” of the rcportal.

To test the rest service: “http://<hostname>/rest/api/v1/” will return a json with the api resources available.


