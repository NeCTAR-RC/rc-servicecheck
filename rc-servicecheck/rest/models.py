from django.db import models


class Contact(models.Model):
    """
    A model for containing contact data.
    """
    id = models.AutoField(primary_key=True,
                          max_length=255, blank=False, null=False)
    username = models.CharField(max_length=255, blank=False,  null=False)
    alias = models.CharField(max_length=255, blank=False,  null=False)
    email = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=False, null=False)

    def name(self):
        if self.email is None:
            return self.username
        else:
            return self.username + '-' + self.email

    def group_name(self):
        return self.name() + '_GROUP'

    def __unicode__(self):
        return str(self.name())


class Host(models.Model):
    """
    A model for containing host data.
    """
    id = models.AutoField(primary_key=True,
                          max_length=255, blank=False, null=False)
    host_ip = models.CharField(max_length=255,
                               blank=False, null=False)
    token = models.CharField(max_length=255, blank=False, null=False)

    def __unicode__(self):
        return str(self.host_ip)


class Monitoring(models.Model):
    """
    A model for containing monitoring data on a given host and contact.
    """
    host = models.ForeignKey(Host)
    contact = models.ForeignKey(Contact)

    name = models.CharField(null=False, blank=False, max_length=255)

    creator_name = models.CharField(null=False, blank=False, max_length=100)
    creator_email = models.CharField(null=False, blank=False, max_length=1000)

    enabled = models.BooleanField(default=True)

    ssh = models.BooleanField(default=False)
    http = models.BooleanField(default=False)
    https = models.BooleanField(default=False)
    smtp = models.BooleanField(default=False)
    hdd_usage = models.BooleanField(default=False)
    mysql = models.BooleanField(default=False)
    postgres = models.BooleanField(default=False)
    cpu_load = models.BooleanField(default=False)

    def __unicode__(self):
        name = self.host.host_ip

        if self.contact is not None:
            name += ' ' + self.contact.username

        return name
