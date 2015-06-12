from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from tastypie.serializers import Serializer
from api.resources import MonitoringResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(MonitoringResource())
v1_api.serializer = Serializer(formats=['json'])

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)
