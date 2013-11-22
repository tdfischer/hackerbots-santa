from django.conf.urls import patterns, include, url

urlpatterns = patterns('santa.exchange',
    url (r'^join/(?P<hash>.+)', 'views.join', name='join'),
)
