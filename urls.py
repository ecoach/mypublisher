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
    url(r'^run_checkout/', login_required(run_checkout_view), name='run_checkout'),
    url(r'^checkout/', login_required(checkout_view), name='checkout'),
    url(r'^checkback/', login_required(checkback_view), name='checkback'),
    url(r'^copycat/', login_required(copycat_view), name='copycat'),
    url(r'^message_review/(?P<msg_id>.*)/$', login_required(message_review_view), name='message_review'),
    url(r'^message_review/', login_required(message_review_view), kwargs={'msg_id':'home'}, name='message_review'),
    #url(r'^survey_review/', login_required(survey_review_view), name='survey_review'),
    url(r'^', login_required(run_checkout_view), name='default'),
)

