from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.simple import redirect_to
from haystack.views import search_view_factory
from piston.resource import Resource
from dhistory.frontpages.views import *
from dhistory.frontpages.handlers import AutocompleteHandler
from dhistory.querypic.views import ExploreView
from dhistory.querypic.forms import ExploreForm

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

autocomplete_resource = Resource(handler=AutocompleteHandler)

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
    url(r'^frontpages/all/(?P<category>(article|advertising|lists|family|literature|illustrated))/$', show_years_words),
    url(r'^frontpages/all/(?P<category>(article|advertising|lists|family|literature|illustrated))/(?P<total_type>(number|words))/$', show_years_words),
    url(r'^frontpages/(?P<newspaper_id>\d+)/$', show_newspaper),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/$', show_newspaper_year),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', show_newspaper_month),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', show_newspaper_issue),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<total_type>(number|words|illustrated))/$', show_newspaper_line),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<total_type>(number|words|illustrated))/$', show_newspaper_year_line),
    url(r'^frontpages/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<total_type>(number|words|illustrated))/$', show_newspaper_month_line),
    url(r'^frontpages/autocomplete/$', autocomplete_resource),
    url(r'^frontpages/autocomplete/(?P<newspaper_id>\d+)/$', autocomplete_resource),
    url(r'^frontpages/autocomplete/(?P<newspaper_id>\d+)/(?P<year>\d{4})/$', autocomplete_resource),
    url(r'^frontpages/autocomplete/(?P<newspaper_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', autocomplete_resource),
)
urlpatterns += patterns('dhistory.rsviewer.views',
    url(r'^archives/naa/$', 'show_naa_home'),
    url(r'^archives/naa/connectors/$', 'show_naa_connectors'),
    url(r'^archives/naa/items/(?P<barcode>\d+)/$', 'show_wall'),
    url(r'^archives/naa/items/(?P<barcode>\d+)/(?P<page>\d+)/$', 'show_naa_page'),
    url(r'^archives/naa/items/(?P<barcode>\d+)/wall/$', redirect_to, {'url': '/archives/naa/items/%(barcode)s/'}),
    url(r'^archives/naa/items/(?P<barcode>\d+)/wall/$', 'show_wall'),
    url(r'^archives/naa/items/(?P<barcode>\d+)/print/$', 'show_printing'),
    url(r'^archives/naa/images/(?P<barcode>\d+)/(?P<page>\d+)/$', 'get_naa_image'),
    url(r'^archives/naa/images/(?P<barcode>\d+)/(?P<page>\d+)/large/$', 'get_naa_image', {'size': 'large'}),
)
urlpatterns += patterns('dhistory.querypic.views',
    url(r'^querypic/$', 'show_home'),
    url(r'^querypic/help/$', 'show_help'),
    url(r'^querypic/create/$', 'show_querypic_form'),
    url(r'^querypic/explore/$', search_view_factory(
        view_class=ExploreView,
        template='querypic-browse.html',
        form_class=ExploreForm
    ), name='haystack_search'),
    url(r'^querypic/(?P<short_url>[a-z0-9]+)/$', 'show_querypic'),
)
urlpatterns += patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'home.html'}, name='home'),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
