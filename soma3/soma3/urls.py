from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^urqa$', 'urqa.views.index'),
	url(r'^urqa/user/new$', 'urqa.views.adduser'),
	url(r'^urqa/posttest$', 'urqa.views.posttest'),
    url(r'^urqa/client/connect$', 'client.views.connect'),
    url(r'^urqa/client/send/exception', 'client.views.receive_exception'),
    url(r'^urqa/client/send/uncaught$', 'client.views.receive_uncaught'),
    url(r'^urqa/client/send/eventpath$', 'client.views.receive_eventpath'),
	 url(r'^urqa/client/test$', 'client.db.receive_ErrorData'),
    # Examples:
    # url(r'^$', 'soma4.views.home', name='home'),
    # url(r'^soma4/', include('soma4.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
