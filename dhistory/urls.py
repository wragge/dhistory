from django.conf.urls import patterns, include, url
from dhistory.frontpages.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dhistory.views.home', name='home'),
    # url(r'^dhistory/', include('dhistory.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^frontpages/$', show_home),
    url(r'^frontpages/all/$', show_years_words),
    url(r'^frontpages/(?P<newspaper_id>\d+)/$', show_newspaper),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/$', show_newspaper_year),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', show_newspaper_month),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', show_newspaper_issue),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<total_type>(number|words))/$', show_newspaper_line),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<total_type>(number|words))/$', show_newspaper_year_line),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<total_type>(number|words))/$', show_newspaper_month_line),
)
urlpatterns += patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'home.html'}, name='home'),
)