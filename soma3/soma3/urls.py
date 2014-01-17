# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from soma3 import settings
from django.views.generic import RedirectView
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #test page
    url(r'^$', RedirectView.as_view(url='/urqa/')),
    url(r'^urqa/$', 'urqa.views.index'),
    url(r'^urqa/posttest$', 'urqa.views.posttest'),
    url(r'^urqa/fileuploadtest$', 'urqa.views.fileuploadtest'),
    url(r'^urqa/cleanup$', 'urqa.views.cleanup'),

    #client module
    url(r'^urqa/client/connect$', 'client.views.connect'),
    url(r'^urqa/client/send/exception$', 'client.views.receive_exception'),
    url(r'^urqa/client/send/exception/native$', 'client.views.receive_native'),
    url(r'^urqa/client/send/exception/dump/(?P<idinstance>\d+)$', 'client.views.receive_native_dump'),
    url(r'^urqa/client/send/exception/log/(?P<idinstance>\d+)$', 'client.views.receive_exception_log'),
    #url(r'^urqa/client/send/eventpath/(?P<idsession>\d+)$', 'client.views.receive_eventpath'),
    #url(r'^urqa/client/send/eventpath/(?P<idsession>.+)$', 'client.views.receive_eventpath'),
    url(r'^urqa/client/send/eventpath$', 'client.views.receive_eventpath'),

    #user manage
    url(r'^urqa/user/registration$', 'usermanage.views.registration'),
    url(r'^urqa/user/delete$', 'usermanage.views.delete_req'),
    url(r'^urqa/user/login$', 'usermanage.views.login_req'),
    url(r'^urqa/user/logout$', 'usermanage.views.logout_req'),

    #oauth module
    url(r'^urqa/user/login_by_google$', 'oauth.views.login_by_google'),
    url(r'^urqa/user/auth_return/$', 'oauth.views.auth_return'),

    #project-list
    url(r'^urqa/projects$', 'projectmanage.views.projects'),

    #project manage
    url(r'^urqa/project/registration$', 'projectmanage.views.registration'),
    url(r'^urqa/project/(?P<apikey>.{8})/delete$', 'projectmanage.views.delete_req'),
    url(r'^urqa/project/(?P<apikey>.{8})/modify$', 'projectmanage.views.modify_req'),
    url(r'^urqa/project/(?P<apikey>.{8})/$', 'projectmanage.views.projectdashboard'),
    url(r'^urqa/project/(?P<apikey>.{8})/dailyes/$', 'projectmanage.views.dailyesgraph'),
    url(r'^urqa/project/(?P<apikey>.{8})/typees/$', 'projectmanage.views.typeesgraph'),
    url(r'^urqa/project/(?P<apikey>.{8})/typees/color$', 'projectmanage.views.typeescolor'),
    url(r'^urqa/project/(?P<apikey>.{8})/viewer/registration$', 'projectmanage.views.viewer_registration'),
    url(r'^urqa/project/(?P<apikey>.{8})/viewer/delete$', 'projectmanage.views.viewer_delete'),
    #url(r'^urqa/project/(?P<apikey>.{8})/errorscorelist$', 'projectmanage.views.errorscorelist'),
    #project manage static
    (r'(?:.*?/)?(?P<path>(css|font|js|images)/.+)$', 'urqa.views.mediapathrequest'),
    #tutorial page
    (r'(?:.*?/)?(?P<path>(tutorial)/.+)$', 'urqa.views.tutorialrequest'),


    #errors
    url(r'^urqa/project/(?P<apikey>.{8})/errors/$', 'errors.views.filter_view'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/list$', 'errors.views.error_list'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/appv_ratio$', 'errors.views.appv_ratio'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/osv_ratio$', 'errors.views.osv_ratio'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/$', 'errors.views.errorDetail'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/(?P<idinstance>\d+)$', 'errors.views.instancedetatil'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/(?P<idinstance>\d+)/log$', 'errors.views.log'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/(?P<idinstance>\d+)/instanceeventpath$', 'errors.views.instanceeventpath'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/eventpath$', 'errors.views.eventpath'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/tag/new$', 'errors.views.newTag'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/tag/delete$', 'errors.views.deleteTag'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/comment/new$', 'errors.views.newComment'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/comment/delete$', 'errors.views.deleteComment'),

    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/os$', 'errors.views.os'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/app$', 'errors.views.app'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/device$', 'errors.views.device'),
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/country$', 'errors.views.country'),

    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/status$', 'errors.views.chstatus'),

    #Statistics
    url(r'^urqa/project/(?P<apikey>.{8})/statistics/$', 'statistics.views.statistics'),
    url(r'^urqa/project/(?P<apikey>.{8})/statistics/chartdata', 'statistics.views.chartdata'),

    #symbol
    url(r'^urqa/project/(?P<apikey>.{8})/errors/(?P<iderror>\d+)/symbol/list$', 'errors.views.so_list'),
    url(r'^urqa/project/(?P<apikey>.{8})/symbol/upload$', 'projectmanage.views.so_upload'),

    #proguard map
    url(r'^urqa/project/(?P<apikey>.{8})/proguardmap/upload$', 'projectmanage.views.proguardmap_upload'),
    url(r'^urqa/project/(?P<apikey>.{8})/proguardmap/delete$', 'projectmanage.views.proguardmap_delete'),

    # Examples:
    # url(r'^$', 'soma4.views.home', name='home'),
    # url(r'^soma4/', include('soma4.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()
