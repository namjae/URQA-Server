from django.conf.urls import patterns
from api.views import ProjectList, ProjectDetail

urlpatterns = patterns('',
    (r'^/urqa/projects$', ProjectList.as_view()),
    (r'^/urqa/projects/(?P<pk>\d+)$', ProjectDetail.as_view())
)