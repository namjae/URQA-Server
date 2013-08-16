# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist

from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Errors
from urqa.models import Viewer

def validUserPjtError(username, pid, iderror):

    result, msg, userElement, projectElement = validUserPjt(username,pid)
    if result == False:
        return result, msg, userElement, projectElement, None

    # Project에 Error ID 가 정상적으로 포함되어있는지 확인
    try:
        errorElement = Errors.objects.get(iderror=iderror,pid=projectElement)
    except ObjectDoesNotExist:
        return False, 'Project "%s" have no error id %s' % (pid, iderror), userElement, projectElement, None

    return True, 'success', userElement, projectElement, errorElement


def validUserPjt(username,pid):
    # User가 로그인되어있는지 확인
    try:
        userElement = AuthUser.objects.get(username=username)
    except ObjectDoesNotExist:
        #login url로 이동하
        return False, 'user "%s" not exists' % username, None, None

    # Project가 정상적으로 존재하는지 확인
    try:
        projectElement = Projects.objects.get(pid=pid)
    except ObjectDoesNotExist:
        print 'Fatal error'
        return False, 'Invalid project id %s' % pid, userElement, None

    # User가 Project에 권한이 있는지 확인
    try:
        viewerElement = Viewer.objects.get(uid=userElement, pid=projectElement)
    except ObjectDoesNotExist:
        return False, 'user "%s" have no permission %s' % (username, pid), userElement, projectElement

    return True, 'success', userElement, projectElement