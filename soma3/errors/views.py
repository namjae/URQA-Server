# Create your views here.
# -*- coding: utf-8 -*-

import utility

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Errors
from urqa.models import Viewer
from urqa.models import Tags
from urqa.models import Comments

def validUserPjtError(username, pid, iderror):

    # User가 로그인되어있는지 확인
    try:
        userElement = AuthUser.objects.get(username=username)
    except ObjectDoesNotExist:
        #login url로 이동하
        return 'user "%s" not exists' % username, None, None, None

    # Project가 정상적으로 존재하는지 확인
    try:
        projectElement = Projects.objects.get(pid=pid)
    except ObjectDoesNotExist:
        print 'Fatal error'
        return 'Invalid project id %s' % pid, userElement, None, None

    # User가 Project에 권한이 있는지 확인
    try:
        viewerElement = Viewer.objects.get(uid=userElement, pid=projectElement)
    except ObjectDoesNotExist:
        return 'user "%s" have no permission %s' % (username, pid), userElement, projectElement, None

    # Project에 Error ID 가 정상적으로 포함되어있는지 확인
    try:
        errorElement = Errors.objects.get(iderror=iderror,pid=projectElement)
    except ObjectDoesNotExist:
        return 'Project "%s" have no error id %s' % (pid, iderror), userElement, projectElement, None

    return 'success', userElement, projectElement, errorElement

def newTag(request, pid, iderror):
    msg, userElement, projectElement, errorElement = validUserPjtError(request.user,pid,iderror)

    print msg
    if not errorElement:
        return HttpResponse(msg)

    tag = request.POST['tag']
    tagElement, created = Tags.objects.get_or_create(iderror=errorElement, tag=tag)

    if not created:
        return HttpResponse('tag %s already exists' % tag)
    else:
        return HttpResponse('success')

def deleteTag(request, pid, iderror):
    msg, userElement, projectElement, errorElement = validUserPjtError(request.user, pid, iderror)

    print msg
    if not errorElement:
        return HttpResponse(msg)

    tag = request.POST['tag']
    try:
        #Tags.objects.get(iderror=errorElement, tag=tag).delete()
        tagElement = Tags.objects.get(iderror=errorElement, tag=tag)
        tagElement.delete()
    except ObjectDoesNotExist:
        HttpResponse('tag %s not exists' % tag)



    return HttpResponse('success')



def newComment(request, pid, iderror):
    msg, userElement, projectElement, errorElement = validUserPjtError(request.user,pid,iderror)

    print msg
    if not errorElement:
        return HttpResponse(msg)

    datetime = utility.getDatetime()

    comment = request.POST['comment']
    Comments.objects.create(uid=userElement, iderror=errorElement, datetime=datetime, comment=comment, user=(userElement.first_name + ' ' + userElement.last_name))

    return HttpResponse('success')

def deleteComment(request, pid, iderror):
    msg, userElement, projectElement, errorElement = validUserPjtError(request.user, pid, iderror)

    print msg
    if not errorElement:
        return HttpResponse(msg)

    idcomment = request.POST['idcomment']
    try:
        commentElement = Comments.objects.get(idcomment=idcomment)
        commentElement.delete()
    except ObjectDoesNotExist:
        HttpResponse('comment %s not exists' % idcomment)

    return HttpResponse('success')