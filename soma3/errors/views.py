# Create your views here.
# -*- coding: utf-8 -*-

import utility
import re
import json
import sys

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
from urqa.models import Tags
from urqa.models import Eventpaths

from common import validUserPjt
from common import validUserPjtError

from client.views import calc_eventpath
from errors.detailmodule import manual_auto_determine

def filter_view(request,pid):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('filter.html')
    osv_list = [1,1,1,1]
    appv_list = [1,1,1,1]
    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'osv_list' : osv_list,
        'appv_list' : appv_list,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email,
        'profile_url' : user.image_path,
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

    valid , message , user ,ErrorsElement = author_check_error_page(request.user, pid, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    #manual_Auto
    isManual = True
    if ErrorsElement.autodetermine == 1:
        isManual = False
    else:
        isManual = True

    instanceElements = Instances.objects.filter(iderror = ErrorsElement).order_by('-datetime')
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
    numobins = float(ErrorsElement.numofinstances)

    ###taglist###
    tagsElements = Tags.objects.filter(iderror = ErrorsElement)
    taglist = []
    for tag in tagsElements:
        taglist.append(tag.tag)

    ###callstack###
    callstackstr = ErrorsElement.callstack
    callstackstrlist = callstackstr.split('\n\t')
    counter = 0
    callstacklist = []
    compile = re.compile('\(.*?:[0-9]*?\)')

    for linstr in callstackstrlist:
        tmp = {'counter' : 0, 'source' : '', 'value' : ''}
        counter += 1
        tmp['counter'] = counter
        tmp['value'] = re.sub('\(.*?:[0-9]*?\)','',linstr)
        list = compile.findall(linstr)
        source = ''
        if len(list) > 0:
            source = list[0]
        tmp['source'] = source
        callstacklist.append(tmp)

    ####instance#######
    instancelist = []
    for instance in instanceElements:
        instancetuple = {'datetime' : "", 'osversion' : '','appversion' : '' , 'device' : '', 'country' : '', 'idinstance' : ''}
        instancetuple['datetime'] = instance.datetime.__format__('%Y.%m.%d - %H:%M:%S')
        instancetuple['osversion'] = instance.osversion
        instancetuple['appversion'] = instance.appversion
        instancetuple['device'] = instance.device
        instancetuple['country'] = instance.country
        instancetuple['idinstance'] = instance.idinstance
        instancelist.append(instancetuple)




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
        'Errorswifi' : int(wifi/numobins * 100),
        'Errorsgps' : int(gps/numobins * 100),
        'Errorsmobilenetwork' : int(mobilenetwork/numobins * 100),
        'Errorsmemoryusage' : ErrorsElement.totalmemusage / ErrorsElement.numofinstances,
        'tag_list' : taglist,
        'callstack' : callstacklist,
        'instance_list' : instancelist,
    });
    return HttpResponse(tpl.render(ctx))

def instancedetatil(request, pid, iderror, idinstance):

    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, pid, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    #instance정보
    instance = Instances.objects.filter(idinstance = int(idinstance)).values()
    #dict = instance.objects.values()
    #datetime은 json sealize 안되서 ....

    key_to_remove = 'datetime'
    dict = {key : value for key, value in instance[0].items() if key != key_to_remove}
    dict['datetime'] = instance[0]['datetime'].__format__('%Y.%m.%d - %H:%M:%S')
    result = json.dumps(dict)

    #single 즉 get일땐 __dict__ filter 즉 복수 일땐 obejcts.values() 이것때문에 한시간 날림
    return HttpResponse(result,'application/json')

def log(request, pid, iderror, idinstance):
    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, pid, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    instanceElement = Instances.objects.get(idinstance = int(idinstance))

    logpath = instanceElement.log_path


    logstringlist = []
    try:
        logfile = open(logpath)
        for s in logfile:
            logstringlist.append(s)
    except IOError:
        print 'file read fail'

    print '!!!!!!!log'
    return HttpResponse(json.dumps(logstringlist),'appliacation/json')

#instanceEventpath
def instanceeventpath(request, pid, iderror, idinstance):
    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, pid, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    instanceElement = Instances.objects.get(idinstance = idinstance)

    EventPathElements = Eventpaths.objects.filter(idinstance = instanceElement)

    eventpathlist = []
    for eventpath in EventPathElements:
        eventpathttuple = {'date' : '' , 'time' : '', 'class' : '', 'methodline' : ''}
        eventpathttuple['date'] =eventpath.datetime.__format__('%Y.%m.%d')
        eventpathttuple['time'] =eventpath.datetime.__format__('%H:%M:%S')
        eventpathttuple['class'] = eventpath.classname
        eventpathttuple['methodline'] = str(eventpath.methodname) + ':' + str(eventpath.linenum)
        eventpathlist.append(eventpathttuple)

    return HttpResponse(json.dumps(eventpathlist),'application/json')

#eventpath
def eventpath(request,pid,iderror):

    valid , message , user ,ErrorsElement = author_check_error_page(request.user, pid, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    result = calc_eventpath(ErrorsElement)

    return HttpResponse(result,'application/json')


def author_check_error_page(username,pid,iderror):

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return valid , message , '',''

    try:
        ErrorsElement = Errors.objects.get(iderror = iderror)
    except ObjectDoesNotExist:
        return False, 'DoesNotExist ErrorsElement' , '',''

    return True, 'success' , userelement ,ErrorsElement


