from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'santa.views.index', name='index'),
    url(r'^j/(?P<hash>.+)', 'santa.exchange.views.join', name='join'),
    url(r'^exchange/', include('santa.exchange.urls', namespace='exchange')),
    url(r'^auth/', include('django.contrib.auth.urls', namespace='auth')),
    # url(r'^santa/', include('santa.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
