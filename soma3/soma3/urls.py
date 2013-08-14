from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^urqa$', 'urqa.views.index'),
    url(r'^urqa/posttest$', 'urqa.views.posttest'),
    url(r'^urqa/logintest', 'usermanage.views.logintest'),

    #client module
    url(r'^urqa/client/connect$', 'client.views.connect'),
    url(r'^urqa/client/send/exception$', 'client.views.receive_exception'),
    url(r'^urqa/client/send/exception/log/(?P<idinstance>\d+)$', 'client.views.receive_exception_log'),
    url(r'^urqa/client/send/eventpath$', 'client.views.receive_eventpath'),

    #user manage
    url(r'^urqa/user/registration$', 'usermanage.views.registration'),
    url(r'^urqa/user/delete', 'usermanage.views.delete_req'),
    url(r'^urqa/user/login$', 'usermanage.views.login_req'),
    url(r'^urqa/user/logout$', 'usermanage.views.logout_req'),

    #project manage
    url(r'^urqa/project/registration$', 'projectmanage.views.registration'),
    url(r'^urqa/project/delete$', 'projectmanage.views.delete_req'),

    #errors
    url(r'^urqa/project/(?P<pid>\d+)/errors/(?P<iderror>\d+)/tag/new$', 'errors.views.newtag'),
    url(r'^urqa/project/(?P<pid>\d+)/errors/(?P<iderror>\d+)/tag/delete$', 'errors.views.deletetag'),
    # Examples:
    # url(r'^$', 'soma4.views.home', name='home'),
    # url(r'^soma4/', include('soma4.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
