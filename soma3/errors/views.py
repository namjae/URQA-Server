# Create your views here.
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Errors
from urqa.models import Viewer
from urqa.models import Tags

def validUserPjtError(username, pid, iderror):

    # User가 로그인되어있는지 확인
    try:
        userElement = AuthUser.objects.get(username=username)
    except ObjectDoesNotExist:
        #login url로 이동하
        return None, 'user "%s" not exists' % username

    # Project가 정상적으로 존재하는지 확인
    try:
        projectElement = Projects.objects.get(pid=pid)
    except ObjectDoesNotExist:
        print 'Fatal error'
        return None, 'Invalid project id %s' % pid

    # User가 Project에 권한이 있는지 확인
    try:
        viewerElement = Viewer.objects.get(uid=userElement, pid=projectElement)
    except ObjectDoesNotExist:
        return None, 'user "%s" have no permission %s' % (username, pid)

    # Project에 Error ID 가 정상적으로 포함되어있는지 확인
    try:
        errorElement = Errors.objects.get(iderror=iderror,pid=projectElement)
    except ObjectDoesNotExist:
        return None, 'Project "%s" have no error id %s' % (pid, iderror)

    return errorElement, 'success'

def newtag(request, pid, iderror):
    errorElement, msg = validUserPjtError(request.user,pid,iderror)

    print errorElement, msg
    if not errorElement:
        return HttpResponse(msg)

    tag = request.POST['tag']
    tagElement, created = Tags.objects.get_or_create(iderror=errorElement, tag=tag)

    if not created:
        return HttpResponse('tag %s already exists' % tag)
    else:
        return HttpResponse('success')

def deletetag(request, pid, iderror):
    errorElement, msg = validUserPjtError(request.user, pid, iderror)

    print msg
    if not errorElement:
        return HttpResponse(msg)

    tag = request.POST['tag']
    try:
        tagElement = Tags.objects.get(iderror=errorElement, tag=tag)
    except ObjectDoesNotExist:
        HttpResponse('tag %s not exists' % tag)

    tagElement.delete()

    return HttpResponse('success')