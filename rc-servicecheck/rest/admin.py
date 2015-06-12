from django.contrib import admin
from rest.models import Monitoring, Contact, Host


class HostAdmin(admin.ModelAdmin):
    pass


class ContactAdmin(admin.ModelAdmin):
    pass


class MonitoringAdmin(admin.ModelAdmin):
    pass

admin.site.register(Host, HostAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Monitoring, MonitoringAdmin)
