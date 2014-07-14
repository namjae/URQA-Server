# Create your views here.
# -*- coding: utf-8 -*-


import os
import random
import subprocess
import json
import ast
import datetime
import time
import shutil
import pytz
import sys

#from goto import goto, label

from django.utils.timezone import utc
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Avg
from django.db.models import Q

from common import validUserPjt
from common import getUserProfileDict
from common import getApikeyDict
from common import getSettingDict
from common import ErrorRate_for_color

from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import ProjectSummary
from urqa.models import Viewer
from urqa.models import Sofiles
from urqa.models import Errors
from urqa.models import Appstatistics
from urqa.models import Devicestatistics
from urqa.models import Osstatistics
from urqa.models import Countrystatistics
from urqa.models import Appruncount
from urqa.models import Instances
from urqa.models import Tags
from urqa.models import Comments
from urqa.models import Session
from urqa.models import Sessionevent
from urqa.models import Eventpaths
from urqa.models import Proguardmap
from urqa.models import ErrorsbyApp

#from utility import getTemplatePath
from utility import getTimeRange
from utility import TimeRange
from utility import RANK
from utility import numbertostrcomma
from utility import get_dict_value_matchin_key
#from utility import get_dict_value_matchin_number
from utility import getTimezoneMidNight
from utility import Status
from utility import toTimezone
from utility import getUTCawaredatetime
from config import get_config
from soma3.settings import PROJECT_DIR

def newApikey():
    while True:
        apikey = "%08X" % random.randint(1,4294967295)
        if not Projects.objects.filter(apikey=apikey).exists():
            break
    return apikey


def registration(request):
    #step1: login user element가져오기
    try:
        userElement = AuthUser.objects.get(username=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('user "%s" not exists' % request.user)


    categorydata = json.loads(get_config('app_categories'))
    platformdata = json.loads(get_config('app_platforms'))
    stagedata = json.loads(get_config('app_stages'))
    #stagecolordata = json.loads(get_config('app_stages_color'))
    #avgcolordata = json.loads(get_config('avg_error_score_color'))
    countcolordata = json.loads(get_config('error_rate_color'))

    name = request.POST['name']
    platformtxt = request.POST['platform']
    stagetxt = request.POST['stage']
    categorytxt = request.POST['category']


    platform = platformdata[platformtxt]
    stage =  stagedata[stagetxt]
    category= categorydata[categorytxt]
    color = ErrorRate_for_color( countcolordata , 0 )

    #project name은 중복을 허용한다.

    #step2: apikey를 발급받는다. apikeysms 8자리 숫자
    apikey = newApikey()
    print 'new apikey = %s' % apikey
    projectElement = Projects(owner_uid=userElement,apikey=apikey,name=name,platform=platform,stage=stage,category=category,timezone='Asia/Seoul')
    projectElement.save();
    #step3: viwer db에 사용자와 프로젝트를 연결한다.
    Viewer.objects.create(uid=userElement,pid=projectElement)

    return HttpResponse(json.dumps({'success': True , 'prjname' : name , 'apikey' : apikey, 'color' : color , 'platform' : platformtxt,'stage':stagetxt}), 'application/json')

def delete_req(request,apikey):
    print 'project delete request(APIKEY:%s)' % apikey

    try:
        project = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        return HttpResponse('%s not exists' % apikey)

    #Viewerr관계 지우기
    viewers = Viewer.objects.filter(pid=project)
    viewers.delete()

    #appruncount 삭제
    Appruncount.objects.filter(pid=project).delete()

    #Session 삭제
    sessions = Session.objects.filter(pid=project)
    Sessionevent.objects.filter(idsession__in=sessions).delete()
    sessions.delete()

    #so & sym files 삭제
    Sofiles.objects.filter(pid=project).delete()
    sym_path = os.path.join(PROJECT_DIR,get_config('sym_pool_path') + '%s' % project.apikey)
    if os.path.isdir(sym_path):
        shutil.rmtree(sym_path)
    so_path = os.path.join(PROJECT_DIR,get_config('so_pool_path') + '%s' % project.apikey)
    if os.path.isdir(so_path):
        shutil.rmtree(so_path)

    #Errors 삭제
    errors = Errors.objects.filter(pid=project)
    for e in errors:
        print e.iderror
    #Comments 삭제
    Comments.objects.filter(iderror__in=errors).delete()
    #statistics 삭제
    Appstatistics.objects.filter(iderror__in=errors).delete()
    Osstatistics.objects.filter(iderror__in=errors).delete()
    Devicestatistics.objects.filter(iderror__in=errors).delete()
    Countrystatistics.objects.filter(iderror__in=errors).delete()
    #Tags 삭제
    Tags.objects.filter(iderror__in=errors).delete()
    errors.delete()

    #event path삭제
    Eventpaths.objects.filter(iderror__in=errors).delete()

    #Instaice 삭제
    instances = Instances.objects.filter(iderror__in=errors)
    for i in instances:
        if i.dump_path:
            os.remove(i.dump_path)
        if i.log_path:
            os.remove(i.log_path)
    instances.delete()
    #Errors 삭제
    errors.delete()

    #project 삭제
    project.delete()

    return HttpResponse('delete success')

def modify_req(request, apikey):

    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponse(json.dupms({'success' : False , 'message' : 'wrong access'}),'application/json')

    #오너가 아니라면 안됨!!
    if(projectelement.owner_uid.id != userelement.id):
        return HttpResponse(json.dupms({'success' : False , 'message' : 'Only the owner'}),'application/json')


    stagedata = json.loads(get_config('app_stages'))
    categorydata = json.loads(get_config('app_categories'))
    platformdata = json.loads(get_config('app_platforms'))

    projectelement.category = categorydata[request.POST['category']]
    projectelement.stage = stagedata[request.POST['stage']]
    projectelement.platform = platformdata[request.POST['platform']]
    projectelement.name = request.POST['projectname']
    projectelement.timezone = request.POST['timezone']

    #project modify
    projectelement.save();
    return HttpResponse(json.dumps({'success' : True , 'message' : 'success modify project'}),'application/json')

def so2sym(projectElement, appver, so_path, filename):
    arg = [os.path.join(PROJECT_DIR,get_config('dump_syms_path')) ,os.path.join(so_path,filename)]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    if stderr.find('no debugging') != -1:
        print stderr
        return False, 0

    vkey =  stdout.splitlines(False)[0].split()[3]
    try:
        sofileElement = Sofiles.objects.get(pid=projectElement, appversion=appver, versionkey=vkey)
    except ObjectDoesNotExist:
        return False, 0

    sym_path = os.path.join(PROJECT_DIR,get_config('sym_pool_path') + '/%s' % projectElement.apikey)
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % appver
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % sofileElement.filename
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % vkey
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    filename = sofileElement.filename + '.sym'
    fp = open(os.path.join(sym_path,filename) , 'wb')
    fp.write(stdout)
    fp.close()

    #sofile이 업로드되었음을 알림
    sofileElement.uploaded = 'O'
    sofileElement.save()
    return True, vkey

def update_error_callstack(projectElement, appversion):
    #print 'update_error_callstack'
    errorElements = Errors.objects.filter(pid=projectElement,rank=RANK.Native)
    for errorElement in errorElements:
        if not Appstatistics.objects.filter(iderror=errorElement,appversion=appversion).exists():
            continue
        #print 'err',errorElement.errorname,errorElement.errorclassname
        instanceElements = Instances.objects.filter(iderror=errorElement,appversion=appversion)
        if not instanceElements.exists():
            continue
        #error중에 첫번째 인스턴스의 콜스텍만 사용함
        instanceElement = instanceElements[0]
        print instanceElement.iderror
        sym_pool_path = os.path.join(PROJECT_DIR,os.path.join(get_config('sym_pool_path'),str(projectElement.apikey)))
        sym_pool_path = os.path.join(PROJECT_DIR,os.path.join(sym_pool_path, instanceElement.appversion))
        arg = [os.path.join(PROJECT_DIR,get_config('minidump_stackwalk_path')) , instanceElement.dump_path, sym_pool_path]
        print arg
        fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = fd_popen.communicate()

        #print 'yhc_stdout',stdout
        cs_flag = 0
        stdout_split = stdout.splitlines()
        for line in stdout_split:
            if line.find('(crashed)') != -1:
                callstack = line + '\n'
                cs_flag = cs_flag + 1
            elif cs_flag:
                if line.find('Thread') != -1 or cs_flag >= 40:
                    break;
                callstack += line + '\n'
                cs_flag = cs_flag + 1
        errorElement.callstack = callstack
        errorElement.save()
        print errorElement.errorname
        print errorElement.errorclassname
        #print callstack
        #print '','',''
    return True

def extractinfo(projectElement,temp_path,temp_fname):
    print projectElement,temp_path,temp_fname

    arg = [os.path.join(PROJECT_DIR,get_config('dump_syms_path')) ,os.path.join(temp_path,temp_fname)]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    if stderr.find('no debugging') != -1:
        print stderr
        return False, '0', '0', 'No debug info'

    vkey =  stdout.splitlines(False)[0].split()[3]
    print 'uploaded version key = ',vkey

    try:
        sofile = Sofiles.objects.get(pid=projectElement,versionkey=vkey)
    except ObjectDoesNotExist:
        print 'invalid sofile'
        return False, '0', '0', 'Invalid sofile'

    return True, sofile.appversion, sofile.filename, 'Success'

def so_upload(request, apikey):
    #print request
    print 'so_upload',apikey

    #appver = request.POST['version']

    #print 'appversion',appver

    result, msg, userElement, projectElement = validUserPjt(request.user, apikey)

    #update_error_callstack(projectElement,appver)

    if not result:
        return HttpResponse(msg)
    print request.method
    print request.FILES
    print request.POST

    retdat = {'result':-1,'msg':'Failed to Upload File'}

    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            temp_fname = file._name

            temp_path = os.path.join(PROJECT_DIR,get_config('so_pool_path') +'/%s' % apikey)
            if not os.path.isdir(temp_path):
                os.mkdir(temp_path)

            temp_path = temp_path + '/temp'# % appver
            if not os.path.isdir(temp_path):
                os.mkdir(temp_path)

            fp = open(os.path.join(temp_path,temp_fname) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()

            flag, appver, so_fname, msg = extractinfo(projectElement,temp_path,temp_fname)
            if flag:
                print appver, so_fname
            else:
                os.remove(os.path.join(temp_path, temp_fname))
                retdat = {'result':-1,'msg':msg}
                print 'so_upload',retdat['result'], retdat['msg']
                return HttpResponse(json.dumps(retdat), 'application/json');
            #if 1:
            #    return HttpResponse('Failed to Upload File')

            so_path = os.path.join(PROJECT_DIR,get_config('so_pool_path') +'/%s' % apikey)
            if not os.path.isdir(so_path):
                os.mkdir(so_path)
            so_path = so_path + '/%s' % appver
            if not os.path.isdir(so_path):
                os.mkdir(so_path)
            print so_path
            os.rename(os.path.join(temp_path,temp_fname),os.path.join(so_path,so_fname))

            #file move
            success_flag,vkey = so2sym(projectElement, appver, so_path, so_fname)
            print 'success_flag',success_flag

            os.remove(os.path.join(so_path, so_fname))#사용한 sofile 삭제, sym파일만 추출하면 so파일은 삭제해도 됨
            if success_flag:
                #정상적으로 so파일이 업로드되었기 때문에 error들의 callstack 정보를 갱신한다.
                update_error_callstack(projectElement,appver)
                retdat = {'result':0,'msg':'File successfully Uploaded, and Valid so file','vkey':vkey}
                print 'so_upload',retdat['result'], retdat['msg']
                return HttpResponse(json.dumps(retdat), 'application/json');
            else:
                retdat = {'result':-1,'msg':'Error, this file have no debug info'}
                print 'so_upload',retdat['result'], retdat['msg']
                return HttpResponse(json.dumps(retdat), 'application/json');

    print 'so_upload',retdat['result'], retdat['msg']
    return HttpResponse(json.dumps(retdat), 'application/json');

def proguardmap_upload(request, apikey):
    print 'proguardmap_upload',apikey

    result, msg, userElement, projectElement = validUserPjt(request.user, apikey)

    if not result:
        return HttpResponse(msg)
    print request.FILES

    appver = request.POST['appversion']
    retdat = {'result':-1,'msg':'Failed to Upload File'}

    if request.method != 'POST':
        retdat = {'result':-1,'msg':'Bad request'}
    elif len(appver) == 0:
        retdat = {'result':-1,'msg':'Invalid App version'}
    elif not 'file' in request.FILES:
        retdat = {'result':-1,'msg':'You should select file'}
    else:
        file = request.FILES['file']
        temp_fname = file._name

        temp_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)
        temp_path = os.path.join(temp_path,apikey)
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)
        temp_path = os.path.join(temp_path,appver)
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)

        fp = open(os.path.join(temp_path,temp_fname) , 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        retdat = {'result':0,'msg':'File successfully Uploaded'}

    if retdat['result'] == 0:
        try:
            mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appver)
            if mapElement.filename != temp_fname:
                temp_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
                temp_path = os.path.join(temp_path,apikey)
                temp_path = os.path.join(temp_path,appver)
                os.remove(os.path.join(temp_path,mapElement.filename))
            mapElement.filename = temp_fname
            mapElement.uploadtime = getUTCawaredatetime()
            mapElement.save()
            retdat = {'result':1,'msg':'File successfully re Uploaded'}
            print 'mapping file overwrite'
        except ObjectDoesNotExist:
            print 'new mapping file'
            mapElement = Proguardmap(
                pid=projectElement,
                appversion=appver,
                filename=temp_fname,
                uploadtime=getUTCawaredatetime(),
            )
            mapElement.save();
        retdat['appversion'] = mapElement.appversion
        retdat['filename'] = mapElement.filename
        retdat['date'] = toTimezone(mapElement.uploadtime,projectElement.timezone).__format__('%Y.%m.%d')
        retdat['time'] = toTimezone(mapElement.uploadtime,projectElement.timezone).__format__('%H:%M')
    print retdat
    return HttpResponse(json.dumps(retdat), 'application/json');

def proguardmap_delete(request,apikey):
    result, msg, userElement, projectElement = validUserPjt(request.user, apikey)

    appversion = request.POST['appversion']
    filename = request.POST['filename']

    try:
        mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion,filename=filename)
        temp_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        temp_path = os.path.join(temp_path,apikey)
        temp_path = os.path.join(temp_path,appversion)
        os.remove(os.path.join(temp_path,filename))
        mapElement.delete();
        retdat = {'result':0,'msg':'Success'}
    except ObjectDoesNotExist:
        retdat = {'result':-1,'msg':'Invalid delete request'}
    return HttpResponse(json.dumps(retdat), 'application/json');


def projects(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/urqa/')

    project_list = []

    stagedata = json.loads(get_config('app_stages'))
    #stagecolordata = json.loads(get_config('app_stages_color'))
    #avgcolordata = json.loads(get_config('avg_error_score_color'))
    countcolordata = json.loads(get_config('error_rate_color'))
    platformdata = json.loads(get_config('app_platforms'))

    if request.user.is_superuser:
        #Super User일 경우 모든 프로젝트 보이기
        MergeProjectElements = ProjectSummary.objects.all()

        for idx, project in enumerate(MergeProjectElements):
            projectdata = {}
            projectdata['apikey'] = project.apikey
            stagetxt = get_dict_value_matchin_key(stagedata,project.stage)
            projectdata['count'] =  project.instanceCount
            errorRate = int(project.instanceCount * 100 / project.runcount)
            projectdata['color'] = ErrorRate_for_color( countcolordata , errorRate )
            projectdata['name'] = project.name
            projectdata['platform'] = get_dict_value_matchin_key(platformdata,project.platform).lower()
            projectdata['stage'] = stagetxt
            project_list.append(projectdata)

    else:
        #주인인 project들
        UserElement = AuthUser.objects.get(username = request.user)
        OwnerProjectElements = Projects.objects.filter(owner_uid = UserElement.id)

        ViewerElements = Viewer.objects.filter(uid = UserElement.id).values('pid')
        ViewerProjectElements = Projects.objects.filter(pid__in = ViewerElements)
        MergeProjectElements = OwnerProjectElements | ViewerProjectElements


    #print MergeProjectElements



        for idx, project in enumerate(MergeProjectElements):
            projectdata = {}
            projectdata['apikey'] = project.apikey
            #stage color 구하기
            stagetxt = get_dict_value_matchin_key(stagedata,project.stage)
            #projectdata['color'] = stagecolordata.get(stagetxt)

            week, today = getTimeRange(TimeRange.weekly,project.timezone)#최근 7일이내것만 표시

            errorElements = Errors.objects.filter(pid = project.pid, status__in = [Status.New,Status.Open])
            instanceCount = Instances.objects.filter(iderror__in=errorElements,datetime__range = (week, today)).count()
            apprunCount = Appruncount.objects.filter(pid=project.pid,date__range = (week, today)).aggregate(apprunCount=Sum('runcount'))['apprunCount']
            #print instanceCount
            #print '(week, today)',project.pid,(week, today)
            #print Appruncount.objects.filter(pid=project.pid,date__gte = week)
            #print apprunCount
            projectdata['count'] =  instanceCount
            if not apprunCount:
                errorRate = 0
            else:
                errorRate = int(instanceCount * 100.0 / apprunCount)

            #print project.name, 'errorRate %d%%' % errorRate, instanceCount, apprunCount
            #Avg ErrorScore에 대한 컬러
            projectdata['color'] = ErrorRate_for_color( countcolordata , errorRate )
            #print projectdata['color']

            projectdata['name'] = project.name
            projectdata['platform'] = get_dict_value_matchin_key(platformdata,project.platform).lower()
            projectdata['stage'] = stagetxt
            project_list.append(projectdata)



    

    categorydata = json.loads(get_config('app_categories'))
    platformdata = json.loads(get_config('app_platforms'))
    stagedata = json.loads(get_config('app_stages'))

    ctx = {
        # 'project_list' : project_list ,
        'project_list' : project_list,
        'app_platformlist' : platformdata.items(),
        'app_categorylist' : categorydata.items(),
        'app_stagelist' : stagedata.items()
    }



    return render(request, 'project-select.html', ctx)

def projectdashboard(request, apikey):

    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponseRedirect('/urqa')

    print request.META.get('REMOTE_ADDR'),username, projectelement.name

    userdict = getUserProfileDict(userelement)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,userelement)

    listdict = errorscorelist(apikey)

    dashboarddict = {
        'error_list' : listdict,
        'total_error_counter' :  len(listdict)
    }

    ctx = dict(userdict.items() + apikeydict.items() + settingdict.items() + dashboarddict.items() )

    return render(request, 'projectdashboard.html', ctx)

def dailyesgraph(request, apikey):

    default = {
        "max":{"key":5, "value":0},
        "tags":[
            ]
        }

    retention = TimeRange.weekly #7일치 데이터를 보여줌
    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponse(json.dumps(default),'application/json')

    sql = "select count(*) as errorcount ,appversion, DATE_FORMAT(CONVERT_TZ(datetime,'UTC',%(timezone)s),'%%y-%%m-%%d') as errorday "
    sql = sql + "from instances A, errors B "
    sql = sql + "where A.iderror = B.iderror "
    sql = sql + "and pid = %(pidinput)s "
    sql = sql + "and B.status in (0,1) "
    sql = sql + "and A.datetime > %(pasttime)s"
    sql = sql + "group by errorday"

    past, today = getTimeRange(retention,projectElement.timezone)

    params = {'timezone':projectElement.timezone,'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}
    places = ErrorsbyApp.objects.raw(sql, params)

    maxvalue = 0
    value = {'key' : 0 , 'value' : 0}
    for i in range(retention-1,-1,-1):
        day1 = getTimezoneMidNight(projectElement.timezone) + datetime.timedelta(days =  -i)
        #print >> sys.stderr,'day',day1,day1.month,day1.day,day1.hour,day1.minute
        #print >> sys.stderr,'utc',toTimezone(day1,'UTC')

        instanceCount = 0
        for idx, pl in enumerate(places):
            if day1.strftime('%y-%m-%d') == pl.errorday:
                instanceCount = pl.errorcount
                break;
        value = {'key' : 0 , 'value' : instanceCount}
        if maxvalue < instanceCount:  #maxvalue!
                maxvalue = instanceCount
        value['key'] = day1.strftime('%m / %d')
        default['tags'].append(value)
    default['max']['key'] = len(default['tags'])
    default['max']['value'] = maxvalue

    return HttpResponse(json.dumps(default),'application/json')

def typeesgraph(request, apikey):

    #print >> sys.stderr,'typeesgraph'
    #프로젝트 ID에 맞는 에러들을 가져오기 위함
    default = {
        "tags":[
            {"key":"Unhandle", "value":0},
            {"key":"Native", "value":0},
            {"key":"Critical", "value":0},
            {"key":"Major", "value":0},
            {"key":"Minor", "value":0},
            ]
        }

    try:
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        #print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json')

    retention = TimeRange.weekly
    past, today = getTimeRange(retention,projectElement.timezone)


    sql = 'select B.iderror as iderrorbyrank, count(*) as errorcount, rank as errorrank '
    sql = sql + ' from instances A, errors B '
    sql = sql + ' where A.iderror = B.iderror '
    sql = sql + ' and B.status in (0,1) '
    sql = sql + ' and B.pid = %(pidinput)s and datetime > %(pasttime)s'
    sql = sql + ' group by errorrank'

    params = {'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}
    places = ErrorsbyApp.objects.raw(sql, params)

    for i in range(RANK.Unhandle,RANK.Minor+1):
        for idx, pl in enumerate(places):
            if pl.errorrank == i:
                default['tags'][i]['value'] = pl.errorcount
                break
            #print >> sys.stderr,pl.iderrorbyrank,pl.errorcount,pl.errorrank
    popcount = RANK.Unhandle
    for i in range(RANK.Unhandle,RANK.Minor+1):
        if default['tags'][i-popcount]['value'] == 0:
            default['tags'].pop(i-popcount)
            popcount += 1

   
    result = json.dumps(default)
    return HttpResponse(result,'application/json')

def typeescolor(request ,apikey):

    timerange = TimeRange.weekly

    #print >> sys.stderr,'typeescolor'

    default = {
        "tags":[
            {"key":"Unhandle", "value":0},
            {"key":"Critical", "value":0},
            {"key":"Major", "value":0},
            {"key":"Minor", "value":0},
            {"key":"Native", "value":0}
            ]
        }

    #프로젝트 ID에 맞는 에러들을 가져오기 위함
    try:
        ProjectElement = Projects.objects.get(apikey= apikey)
    except ObjectDoesNotExist:
        #print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json')

    week , today = getTimeRange(timerange,ProjectElement.timezone)

    for i in range(RANK.Unhandle,RANK.Minor+1): # unhandled 부터 Minor 까지
       ErrorsElements = Errors.objects.filter(pid = ProjectElement ,status__in=[Status.New,Status.Open] ,lastdate__range = (week,today), rank = i) #일주일치 얻어옴
       if len(ErrorsElements) > 0:
           for error in ErrorsElements:
               default['tags'][i]['value'] += error.errorweight
               #print str(i) + ':' +  str(default['tags'][i]['value'])

    ColorTable = []
    for i in range(RANK.Unhandle,RANK.Minor+1):
        if default['tags'][i]['value'] != 0:
            ColorTable.append(RANK.rankcolorbit[i])

    result = json.dumps(ColorTable)
    print >>sys.stderr,'ColorTable',ColorTable
    return HttpResponse(result,'application/json')

#name, file, tag, counter
def errorscorelist(apikey):



    try:
        ProjectElement = Projects.objects.get(apikey = apikey)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse('')

    #print today

    week, today = getTimeRange(TimeRange.weekly,ProjectElement.timezone)
    ErrorElements = Errors.objects.filter(pid = ProjectElement , status__in=[Status.New,Status.Open],lastdate__range = (week, today) ).order_by('rank','-numofinstances','-lastdate')

    jsondata = []


    for error in ErrorElements:
        #if error.rank == RANK.Suspense:
            #continue
        TagElements = Tags.objects.filter(iderror = error)

        rankcolor = ''
        if error.rank == -1:
            rankcolor = 'none'
        else:
            rankcolor = RANK.rankcolor[error.rank]

        dicerrordata = {
            'ErrorName' : error.errorname ,
            #'ErrorClassName' : error.errorclassname + '(' + error.linenum + ')' ,
            'ErrorClassName' : error.errorclassname + ':' + error.linenum,
            'tags': TagElements,
            'ErrorCount' : error.numofinstances,
            'Errorid' : error.iderror ,
            'Errorrankcolor' : rankcolor,
            'ErrorDateFactor' : error.gain1,
            'ErrorQuantityFactor' : error.gain2
        }
        jsondata.append(dicerrordata);

        #print dicerrordata
        Viewer.objects.create

    return jsondata



def viewer_registration(request,apikey):

    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponse(json.dumps({'success' : False, 'username' : '' ,'message' : 'Wrong Access' } ),'application/json')

    registusername = request.POST['username']


    #존재하지 않으면 fail
    user = AuthUser.objects.filter(username__exact=registusername)
    if not user.exists():
        return HttpResponse(json.dumps({'success' : False, 'username' : '' , 'message' : 'not exists user name' } ),'application/json')


    viewerElement = Viewer(uid = user[0], pid = projectelement)
    viewerElement.save()

    return HttpResponse(json.dumps({'success': True, 'username' : registusername , 'message' : 'success registration'}),'application/json')

def viewer_delete(request,apikey):

    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponse(json.dumps({'success' : False, 'username' : '' } ),'application/json')

    deleteusername = request.POST['username']

    try:
        deleteuser = AuthUser.objects.get(username = deleteusername)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'success' : False, 'username' : '' } ),'application/json')


    try:
        deleteviewtuple = Viewer.objects.get(pid = projectelement.pid , uid = deleteuser.id)
        deleteviewtuple.delete()
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'success' : False, 'username' : '' } ),'application/json')

    return HttpResponse(json.dumps({'success' : True, 'username' : deleteusername } ),'application/json')
