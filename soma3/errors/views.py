# Create your views here.
# -*- coding: utf-8 -*-

import utility

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, loader
from django.http import HttpResponseRedirect

from urqa.models import Tags
from urqa.models import Comments
from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Instances

from common import validUserPjt
from common import validUserPjtError

from errors.detailmodule import manual_auto_determine

def filter_view(request,pid):



    tpl = loader.get_template('filter.html')
    osv_list = [1,1,1,1]
    appv_list = [1,1,1,1]
    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'osv_list' : osv_list,
        'appv_list' : appv_list,
    });
    return HttpResponse(tpl.render(ctx))


def newTag(request, pid, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user,pid,iderror)

    print msg
    if not result:
        return HttpResponse(msg)

    tag = request.POST['tag']
    tagElement, created = Tags.objects.get_or_create(iderror=errorElement, tag=tag)

    if not created:
        return HttpResponse('tag %s already exists' % tag)
    else:
        return HttpResponse('success')

def deleteTag(request, pid, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user, pid, iderror)

    print msg
    if not result:
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
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user,pid,iderror)

    print msg
    if not result:
        return HttpResponse(msg)

    datetime = utility.getDatetime()

    comment = request.POST['comment']
    Comments.objects.create(uid=userElement, iderror=errorElement, datetime=datetime, comment=comment, user=(userElement.first_name + ' ' + userElement.last_name))

    return HttpResponse('success')

def deleteComment(request, pid, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user, pid, iderror)

    print msg
    if not result:
        return HttpResponse(msg)

    idcomment = request.POST['idcomment']
    try:
        commentElement = Comments.objects.get(idcomment=idcomment)
        commentElement.delete()
    except ObjectDoesNotExist:
        HttpResponse('comment %s not exists' % idcomment)

    return HttpResponse('success')


def errorDetail(request,pid,iderror):

    #Iderror 잘못되었을시 접근 불가
    try:
        ErrorsElement = Errors.objects.get(iderror = iderror)
    except ObjectDoesNotExist:
        print 'DoesNotExist ErrorsElement'
        return HttpResponseRedirect('/urqa')

    #프로젝트 권한 없을시 접근 불가
    #로그인 안되었을시 접근 불가
    username = request.user
    valid , message , userelement, projectelement = validUserPjt(username,pid)
    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    #manual_Auto
    isManual = True
    if ErrorsElement.autodetermine == 1:
        isManual = False
    else:
        isManual = True

    instanceElements = Instances.objects.filter(iderror = ErrorsElement)
    #wifi
    wifi = 0
    wifielements = instanceElements.filter(wifion = 1)
    wifi = len(wifielements)
    #gps
    gps = 0
    gpselements = instanceElements.filter(gpson = 1)
    gps = len(gpselements)
    #mobilenetwork
    mobilenetwork = 0
    mobilenetworkelements = instanceElements.filter(mobileon = 1)
    mobilenetwork = len(mobilenetworkelements)


    tpl = loader.get_template('details.html')
    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'iderror' : iderror,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email ,
        'ErrorScore' : ErrorsElement.errorweight,
        'isManual' :  isManual,
        'ErrorName' : ErrorsElement.errorname,
        'ErrorFile' : '(' +ErrorsElement.errorclassname + ':' + ErrorsElement.linenum + ')',
        'Errornumofinstances' : ErrorsElement.numofinstances,
        'Errorrecur' : ErrorsElement.recur,
        'Errorstatus' : ErrorsElement.status,
        'Errorswifi' : wifi/ErrorsElement.numofinstances,
        'Errorsgps' : gps/ErrorsElement.numofinstances,
        'Errorsmobilenetwork' : mobilenetwork/ErrorsElement.numofinstances,
        'Errorsmemoryusage' : ErrorsElement.totalmemusage / ErrorsElement.numofinstances,
    });
    return HttpResponse(tpl.render(ctx))