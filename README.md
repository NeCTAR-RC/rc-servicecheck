Nectar Monitoring Django Rest service
-------------------------------------

The backend Rest service that compliments the system service monitoring frontend of the nectar dashboard.

Requirements
------------

- Apache 2
- wsgi_mod - apache module
- Python 2.7
- Django 1.6.5 - python web framework
- Tastypie 0.12.1 - Restful api
- MySQL or Postgres for Django webapp db

Getting Started
---------------

* Run tox to setup the virtualenv
* Set up apache config for web app if deploying to apache web server.
* Set the directory path to where the web app is installed in the 'nectar_monitor_rest/wsgi.py' if deploying to apache.
* If using MySQL or Postgres, setup a new db(Ignore this step if using sqlite).
* Set the database connection in the 'nectar_monitor_rest/settings.py'.
* Run 'manage.py syncdb' to generate the data tables(for sqlite it will create db file). Create a super user when prompt.
* To test system run in dev/debug mode with 'manage.py runserver' or if deployed to apache web server restart apache and go to 'http://<web host>/rest/api/v1/', you should get a list of available resources of the rest server.

Setting up an api_key
---------------------

An API Key is used to authenticate clients to the monitoring service. With each RESTful request, an user account name coupled with a secret token is sent in the header.

Multiple keys can exist to many users allowing each access to the service.

To create a new key,

* Run django app in dev/debug mode using 'manage.py runserver' or on apache webserver
* Log into the admin page with the super user account. (http://<web host>/rest/admin/)
* Create a new user, this will generate an api key used to authenticate the rest. You can check the api_key under 'Tastypie'. The username and api_key will be used to authenticate rest calls.

Using the remove_tenant.py command
----------------------------------

In the root directory of the project is the remove_tenant.py script.
This is used to remove all monitoring checks for a specified tenant ID.

To use script:
* To run: $ remove_tenant.py -t <tenantID>
* For help: $ remove_tenant.py -h

RESTful requests
----------------

There a 6 requests available - 4 GET, 1 POST, 1 PUT and 1 DELETE. They are all related to performing operations on a monitored server/s.

---------------------------------------------------------------------------
Method: GET
URL: http://<web host>/rest/api/v1/monitoring/<monitoring id>?tenantID=<tenant id>
Params: <monitoring id> The ID of the monitoring to be fetched
        <tenant id> The ID of the tenant associated to the monitoring
Output Type: JSON
Description: Returns all data on the monitoring object
Example Output:
{
    "id": 1,
    "name": "domain",
    "host": {
        "ip": "domain.org"
    },
    "contact": {
        "email": "contact@domain.org",
        "username": "contact"
    },
    "creatorEmail": "creator@domain.org",
    "creatorName": "creator",
    "enabled": true,
    "cpuLoad": false,
    "hddUsage": false,
    "http": true,
    "https": false,
    "mysql": false,
    "postgres": false,
    "smtp": false,
    "ssh": false,
    "resource_uri": "/rest/api/v1/monitoring/1/",
    "status": {
        "ping": 0,
        "http": 0
    }
}
---------------------------------------------------------------------------

---------------------------------------------------------------------------
Method: POST
URL: http://<web host>/rest/api/v1/monitoring/
Params: None
Output Type: JSON
Description: Creates a new monitoring on a server for a given contact
Example Input:
{
    "host": {
        "ip": "domain.com",
        "name": "domain"
        "enabled": 1,
        "checks": {
            "ssh": 0,
            "http": 0,
            "https": 0,
            "smtp": 0,
            "hddUsage": 0,
            "mysql": 0,
            "postgres": 0,
            "cpuLoad": 0
        }
    },
    "contact": {
        "username": "user",
        "alias": "alias",
        "email": "user@domain.com"
    },
    "creator": {
        "name": "creator",
        "email": "creator@domain.com"
    }
}
---------------------------------------------------------------------------

---------------------------------------------------------------------------
Method: PUT
URL: http://<web host>/rest/api/v1/monitoring/<monitoring id>
Params: <monitoring id> The ID of the monitoring to be updated
Output Type: JSON
Description: Updates an existing monitoring on a server for a given contact
Example Input:
{
    "host": {
        "ip": "domain.com",
        "name": "domain"
        "enabled": 1,
        "checks": {
            "ssh": 0,
            "http": 0,
            "https": 0,
            "smtp": 0,
            "hddUsage": 0,
            "mysql": 0,
            "postgres": 0,
            "cpuLoad": 0
        }
    },
    "contact": {
        "username": "user",
        "alias": "alias",
        "email": "user@domain.com"
    },
    "creator": {
        "name": "creator",
        "email": "creator@domain.com"
    }
}
---------------------------------------------------------------------------

---------------------------------------------------------------------------
Method: DELETE
URL: http://<web host>/rest/api/v1/monitoring/<monitoring id>
Params: <monitoring id> The ID of the monitoring to be deleted
Output Type: None
Description: Deletes an existing monitoring on a server for a given contact
---------------------------------------------------------------------------

---------------------------------------------------------------------------
Method: GET
URL: http://<web host>/api/v1/monitoring/?tenantID=<tenant id>
Params: <tenant id> The ID of the tenant associated to the monitoring
Output Type: JSON
Description: Returns all data on the monitorings associated to the tenant
Example Output:
{
    "objects": [
        {
            "id": 1,
            "name": "domain",
            "host": {
                "ip": "domain.com"
            },
            "contact": {
                "email": "contact@domain.org",
                "username": "contact"
            },
            "creatorEmail": "creator@domain.org",
            "creatorName": "creator",
            "enabled": true,
            "cpuLoad": false,
            "hddUsage": false
            "http": true,
            "https": false,
            "mysql": false,
            "postgres": false,
            "smtp": false,
            "ssh": false,
            "resource_uri": "/rest/api/v1/monitoring/1/",
            "status": {
                "ping": 0,
                "http": 0
            }
        },
        {
            "id": 2,
            "name": "sub-domain",
            "host": {
                "ip": "sub-domain.com"
            },
            "contact": {
                "email": "contact@sub-domain.org",
                "username": "contact"
            },
            "creatorEmail": "creator@sub-domain.org",
            "creatorName": "creator",
            "enabled": true,
            "cpuLoad": false,
            "hddUsage": false
            "http": true,
            "https": true,
            "mysql": false,
            "postgres": false,
            "smtp": false,
            "ssh": false,
            "resource_uri": "/rest/api/v1/monitoring/2/",
            "status": {
                "ping": 0,
                "http": 1,
                "https": 2
            }
        }
    ],
    "meta": {
        "limit": 20,
        "next": null,
        "offset": 0,
        "previous": null,
        "total_count": 2
    },
}
---------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------
Method: GET
URL: http://<web host>/rest/api/v1/monitoring/unsubscribe/?hostToken=<host token>&contactToken=<contact token>
Params: <host token> The token of the host
        <contact token> The token of the contact
Output Type: Text
Description: Removes the current contact email of the monitoring then emails the contact email and monitoring creator of the change
-------------------------------------------------------------------------------------------------------------