from django.conf.urls.defaults import patterns, include, url
from .views import *
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # admin
    #url(r'^admin/', include(admin.site.urls)),

    # publisher urls
    #url(r'^usage_stats/', login_required(_view), name='usage'),
    url(r'^checkout/', login_required(checkout_view), name='checkout'),
    url(r'^checkback/', login_required(checkback_view), name='checkback'),
    url(r'^', login_required(checkout_view), name='default'),

)

