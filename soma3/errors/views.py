# Create your views here.
# -*- coding: utf-8 -*-

import utility
from utility import getTimeRange
from utility import TimeRange

import re
import json
import sys

from utility import Status
from utility import RANK

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, loader
from django.http import HttpResponseRedirect

from urqa.models import Tags
from urqa.models import Comments
from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Projects
from urqa.models import Instances
from urqa.models import Eventpaths
from urqa.models import Osstatistics
from urqa.models import Appstatistics

from common import validUserPjt
from common import validUserPjtError
from common import getUserProfileDict
from common import getApikeyDict
from common import getSettingDict

from utility import get_dict_value_matchin_key
from utility import get_dict_value_matchin_number

from client.views import calc_eventpath
from config import get_config


def newTag(request, apikey, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user,apikey,iderror)

    print msg
    if not result:
        return HttpResponse(msg)

    tag = request.POST['tag']
    tagElement, created = Tags.objects.get_or_create(iderror=errorElement, tag=tag)

    if not created:
        return HttpResponse('tag %s already exists' % tag)
    else:
        return HttpResponse('success')

def deleteTag(request, apikey, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user, apikey, iderror)

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



def newComment(request, apikey, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user,apikey,iderror)

    print msg
    if not result:
        return HttpResponse(msg)

    datetime = utility.getDatetime()

    comment = request.POST['comment']
    Comments.objects.create(uid=userElement, iderror=errorElement, datetime=datetime, comment=comment, user=(userElement.first_name + ' ' + userElement.last_name))

    return HttpResponse('success')

def deleteComment(request, apikey, iderror):
    result, msg, userElement, projectElement, errorElement = validUserPjtError(request.user, apikey, iderror)

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


def errorDetail(request,apikey,iderror):

    valid , message , user ,ErrorsElement = author_check_error_page(request.user, apikey, iderror)
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


    projectelement = Projects.objects.get(apikey = apikey)
    platformdata = json.loads(get_config('app_platforms'))
    #platformtxt = get_dict_value_matchin_key(platformdata,projectelement.platform)



    userdict = getUserProfileDict(user)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,user)

    detaildict = {
        'iderror' : iderror,
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
        'ErrorRankColor' : RANK.rankcolor[ErrorsElement.rank],
        'tag_list' : taglist,
        'callstack' : callstacklist,
        'instance_list' : instancelist,
    }
    ctxdict  = dict(userdict.items() + apikeydict.items() + settingdict.items() + detaildict.items() )

    tpl = loader.get_template('details.html')
    ctx = Context(ctxdict);
    return HttpResponse(tpl.render(ctx))

def instancedetatil(request, apikey, iderror, idinstance):

    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, apikey, iderror)
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

def log(request, apikey, iderror, idinstance):
    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, apikey, iderror)
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
def instanceeventpath(request, apikey, iderror, idinstance):
    #권한 있나 없나 체크
    valid , message , user ,ErrorsElement = author_check_error_page(request.user, apikey, iderror)
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
def eventpath(request,apikey,iderror):

    valid , message , user ,ErrorsElement = author_check_error_page(request.user, apikey, iderror)
    if not valid:
        print message
        return HttpResponseRedirect('/urqa')

    result = calc_eventpath(ErrorsElement)

    return HttpResponse(json.dumps(result),'application/json')


def author_check_error_page(username,apikey,iderror):

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return valid , message , '',''

    try:
        ErrorsElement = Errors.objects.get(iderror = iderror)
    except ObjectDoesNotExist:
        return False, 'DoesNotExist ErrorsElement' , '',''

    return True, 'success' , userelement ,ErrorsElement






def filter_view(request,apikey):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    week, today = getTimeRange(TimeRange.weekly)

    try:
        projectElement = Projects.objects.get(apikey = apikey)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse('')

    errorElements = Errors.objects.filter(pid = projectElement , lastdate__range = (week, today) ).order_by('-errorweight','rank', '-lastdate')
    valid_tag = Tags.objects.filter(iderror__in=errorElements).values('tag').distinct().order_by('tag')
    valid_class = errorElements.values('errorclassname').distinct().order_by('errorclassname')
    valid_app = Appstatistics.objects.filter(iderror__in=errorElements).values('appversion').distinct().order_by('-appversion')
    valid_os = Osstatistics.objects.filter(iderror__in=errorElements).values('osversion').distinct().order_by('-osversion')


    osv_list = []
    os_idx = -1
    prev_v = ['-1','-1','-1']
    for e in valid_os:
        v = e['osversion'].split('.')
        if v[0] != prev_v[0] or v[1] != prev_v[1]:
            prev_v = v
            os_idx += 1
            osv_list.append({})
            osv_list[os_idx]['key'] = '%s.%s' % (v[0],v[1])
            osv_list[os_idx]['value'] = []
        osv_list[os_idx]['value'].append(e['osversion'])


    appv_list = []
    app_idx = -1
    prev_v = ['-1','-1','-1']
    for e in valid_app:
        v = e['appversion'].split('.')
        if v[0] != prev_v[0] or v[1] != prev_v[1]:
            prev_v = v
            app_idx += 1
            appv_list.append({})
            appv_list[app_idx]['key'] = '%s.%s' % (v[0],v[1])
            appv_list[app_idx]['value'] = []
        appv_list[app_idx]['value'].append(e['appversion'])


    tag_list = []
    for e in valid_tag:
        tag_list.append(e['tag'])

    class_list = []
    for e in valid_class:
        class_list.append(e['errorclassname'])

    osv_margin = ''
    for i in range(0,5 - len(osv_list)):
        osv_margin += ' '

    appv_margin = ''
    for i in range(0,5 - len(appv_list)):
        appv_margin += ' '

    tpl = loader.get_template('filter.html')
    filterdict = {
        #'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'tag_list' : tag_list,
        'class_list' : class_list,
        'osv_list' : osv_list,
        'margin' : {'osv':osv_margin,'appv':appv_margin},
        'appv_list' : appv_list,
    }

    userdict = getUserProfileDict(user)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,user)
    print userdict
    ctxdict  = dict(userdict.items() + apikeydict.items() + settingdict.items() + filterdict.items() )
    ctx = Context(ctxdict);

    return HttpResponse(tpl.render(ctx))


def error_list(request,apikey):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponseRedirect('/urqa')
    try:
        projectElement = Projects.objects.get(apikey = apikey)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse(json.dumps({"response":"fail"}), 'application/json');

    jsonData = json.loads(request.POST['json'],encoding='utf-8')

    date = int(jsonData['date'])
    status = int(jsonData['status'])
    rank = jsonData['rank']
    tags = jsonData['tags']
    classes = jsonData['classes']
    appversion = jsonData['appv']
    if appversion and appversion[0] == 'All':
        appversion = []
    osversion = jsonData['osv']
    if osversion and osversion[0] == 'All':
        osversion = []


    week, today = getTimeRange(date)
    errorElements = Errors.objects.filter(pid=projectElement,rank__in=rank,status=status,lastdate__range=(week,today)).order_by('-errorweight','rank', '-lastdate')
    if classes:
        errorElements = errorElements.filter(errorclassname__in=classes)
    if tags:
        tagElements = Tags.objects.select_related().filter(iderror__in=errorElements,tag__in=tags).values('iderror').distinct().order_by('iderror')
        iderror_list = []
        for e in tagElements:
            iderror_list.append(int(e['iderror']))
        if iderror_list:
            errorElements = errorElements.filter(iderror__in=iderror_list)
    if appversion:
        appvElements = Appstatistics.objects.select_related().filter(iderror__in=errorElements,appversion__in=appversion).values('iderror').distinct().order_by('iderror')
        iderror_list = []
        for e in appvElements:
            iderror_list.append(int(e['iderror']))
        if iderror_list:
            errorElements = errorElements.filter(iderror__in=iderror_list)
    if osversion:
        osvElements = Osstatistics.objects.select_related().filter(iderror__in=errorElements,osversion__in=osversion).values('iderror').distinct().order_by('iderror')
        iderror_list = []
        for e in osvElements:
            iderror_list.append(int(e['iderror']))
        if iderror_list:
            errorElements = errorElements.filter(iderror__in=iderror_list)

    print errorElements


    result = []
    for e in errorElements:
        new_e = {}
        new_e['iderror'] = e.iderror
        new_e['rank'] = RANK.toString[e.rank]
        new_e['status'] = Status.toString[e.status]
        new_e['errorname'] = e.errorname
        new_e['errorclassname'] = e.errorclassname
        new_e['linenum'] = e.linenum
        new_e['count'] = e.numofinstances
        new_e['year'] = e.lastdate.year
        new_e['month'] = e.lastdate.month
        new_e['day'] = e.lastdate.day
        new_e['es'] = e.errorweight
        new_e['auto'] = e.autodetermine
        new_e['tags'] = []
        tags = Tags.objects.filter(iderror=e)
        for t in tags:
            new_e['tags'].append(t.tag)
        result.append(new_e)
        #print new_e

    return HttpResponse(json.dumps(result), 'application/json');