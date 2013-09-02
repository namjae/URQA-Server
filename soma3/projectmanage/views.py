# Create your views here.
# -*- coding: utf-8 -*-

import os
import random
import subprocess
import json
import ast
import datetime
import time

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

from common import validUserPjt
from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Viewer
from urqa.models import Sofiles
from urqa.models import Errors
from urqa.models import Appstatistics
from urqa.models import Instances
from urqa.models import Tags
from soma3.settings import STATIC_ROOT
from soma3.settings import STATIC_URL
from utility import getTemplatePath
from utility import getTimeRange
from utility import TimeRange
from utility import RANK
from common import validUserPjt
from urqa.views import index

from config import get_config


def newApikey():
    while True:
        apikey = "%08d" % random.randint(1,99999999)
        if not Projects.objects.filter(apikey=apikey).exists():
            break
    return apikey


def registration(request):
    #step1: login user element가져오기
    try:
        userElement = AuthUser.objects.get(username=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('user "%s" not exists' % request.user)

    name = request.POST['name']
    platform = int(request.POST['platform'])
    stage = int(request.POST['stage'])

    #project name은 중복을 허용한다.

    #step2: apikey를 발급받는다. apikeysms 8자리 숫자
    apikey = newApikey()
    print 'new apikey = %s' % apikey
    projectElement = Projects(owner_uid=userElement,apikey=apikey,name=name,platform=platform,stage=stage)
    projectElement.save();
    #step3: viwer db에 사용자와 프로젝트를 연결한다.
    Viewer.objects.create(uid=userElement,pid=projectElement)

    return HttpResponse('success registration')

def delete_req(request):
    try:
        user = User.objects.get(username__exact=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('%s not exists' % request.user)

    user.delete()

    return HttpResponse('delete success')

def so2sym(projectElement, appver, so_path, filename):
    arg = [get_config('dump_syms_path') ,os.path.join(so_path,filename)]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    if stderr.find('no debugging') != -1:
        print stderr
        return False

    vkey =  stdout.splitlines(False)[0].split()[3]
    try:
        sofileElement = Sofiles.objects.get(pid=projectElement, appversion=appver, versionkey=vkey)
    except ObjectDoesNotExist:
        return False

    sym_path = get_config('sym_pool_path') + '/%s' % projectElement.pid
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % appver
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
    sofileElement.uploaded = 1
    sofileElement.save()
    return True

def update_error_callstack(projectElement, appversion):

    errorElements = Errors.objects.filter(pid=projectElement)
    for errorElement in errorElements:
        if not Appstatistics.objects.filter(iderror=errorElement,appversion=appversion).exists():
            continue
        instanceElements = Instances.objects.filter(iderror=errorElement,appversion=appversion)
        if not instanceElements.exists():
            continue
        instanceElement = instanceElements[0]
        sym_pool_path = os.path.join(get_config('sym_pool_path'),str(projectElement.pid))
        sym_pool_path = os.path.join(sym_pool_path, instanceElement.appversion)
        arg = [get_config('minidump_stackwalk_path') , instanceElement.dump_path, sym_pool_path]
        fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = fd_popen.communicate()

        #print stdout
        cs_flag = 0
        stdout_split = stdout.splitlines()
        for line in stdout_split:
            if line.find('(crashed)') != -1:
                callstack = line + '\n'
                cs_flag = cs_flag + 1
            elif cs_flag:
                if line.find('Thread') != -1 or cs_flag > 40:
                    break;
                callstack += line + '\n'
                cs_flag = cs_flag + 1
        errorElement.callstack = callstack
        errorElement.save()
        print errorElement.errorname
        print errorElement.errorclassname
        print callstack
        print '','',''
    return True

def so_upload(request, pid):

    appver = request.POST['version']

    result, msg, userElement, projectElement = validUserPjt(request.user, pid)

    #update_error_callstack(projectElement,appver)

    if not result:
        return HttpResponse(msg)

    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name

            so_path = get_config('so_pool_path') +'/%s' % pid
            if not os.path.isdir(so_path):
                os.mkdir(so_path)

            so_path = so_path + '/%s' % appver
            if not os.path.isdir(so_path):
                os.mkdir(so_path)

            fp = open(os.path.join(so_path,filename) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()

            success_flag = so2sym(projectElement, appver, so_path, filename)
            if success_flag:
                #정상적으로 so파일이 업로드되었기 때문에 error들의 callstack 정보를 갱신한다.
                update_error_callstack(projectElement,appver)
                return HttpResponse('File Uploaded, and Valid so file')
            else:
                os.remove(os.path.join(so_path, filename))
                return HttpResponse('File Uploaded, but it have no debug info')
    return HttpResponse('Failed to Upload File')


def dashboard(request, pid):



    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)


    ctx = {
        'templatepath' : getTemplatePath(),
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email,
        'profile_url' : user.image_path,
        'error_list' : errorscorelist(pid),
    }
    return render(request, 'projectdashboard.html', ctx)

def dailyesgraph(request, pid):


    #기본 데이터
    default = {
	    "max":{"key":5, "value":0},
	    "tags":[
	        ]
        }

    #프로젝트 ID에 맞는 에러들을 가져오기 위함
    try:
        ProjectElement = Projects.objects.get(apikey= pid)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json');


    #오늘 날짜 및 일주일 전을 계산
    timerange = TimeRange.weekly
    week , today = getTimeRange(timerange)

    #defalut값에 날짜를 대입함
    maxvalue = 0
    for i in range(0,timerange):
        value = {'key' : 0 , 'value' : 0}
        tmpdate = datetime.timedelta(days  = i-(timerange-1) )
        tmpdate = today + tmpdate
        value['key'] = tmpdate.__format__('%m / %d')


        ErrorsElements = Errors.objects.filter(pid = ProjectElement , lastdate__year = tmpdate.year , lastdate__month = tmpdate.month , lastdate__day = tmpdate.day)
        errorweight = 0
        if len(ErrorsElements) > 0:
            for error in ErrorsElements:
                if error.rank == RANK.Suspense:
                    continue
                errorweight += error.errorweight
            value['value'] = errorweight

            if maxvalue < errorweight:  #maxvalue!
                maxvalue = errorweight
        else :
            value['value'] = 0

        default['tags'].append(value)

    default['max']['key'] = len(default['tags'])
    default['max']['value'] = maxvalue

    return HttpResponse(json.dumps(default),'application/json')

def typeesgraph(request, pid):

    timerange = TimeRange.weekly
    week , today = getTimeRange(timerange)


    default = {
        "tags":[
            {"key":"Unhandler", "value":0},
            {"key":"Critical", "value":0},
            {"key":"Major", "value":0},
            {"key":"Minor", "value":0}
            ]
        }

    #프로젝트 ID에 맞는 에러들을 가져오기 위함
    try:
        ProjectElement = Projects.objects.get(apikey= pid)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json')

    print week

    for i in range(RANK.Unhandle,RANK.Minor+1): # unhandled 부터 minor 까지
       ErrorsElements = Errors.objects.filter(pid = ProjectElement , lastdate__range = (week,today), rank = i) #일주일치 얻어옴
       if len(ErrorsElements) > 0:
           for error in ErrorsElements:
               default['tags'][i]['value'] += error.errorweight
               #print str(i) + ':' +  str(default['tags'][i]['value'])

    result = json.dumps(default)
    print result

    return HttpResponse(result,'application/json')

#name, file, tag, counter
def errorscorelist(pid):

    week, today = getTimeRange(TimeRange.weekly)

    try:
        ProjectElement = Projects.objects.get(apikey = pid)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse('')

    #print today

    ErrorElements = Errors.objects.filter(pid = ProjectElement , lastdate__range = (week, today) ).order_by('-errorweight','rank', '-lastdate')

    jsondata = [
    ]


    for error in ErrorElements:
        if error.rank == RANK.Suspense:
            continue
        TagElements = Tags.objects.filter(iderror = error)
        tagString = '';
        for tag in TagElements:
            tagString += tag.tag + ','
            # 마지막 , 제거
            if len(tagString) > 0:
                stringlength = len(tagString)
                tagString = tagString[0 : stringlength - 1]

        dicerrordata = {'ErrorName' : error.errorname ,  'ErrorClassName' : error.errorclassname + '(' + error.linenum + ')' , 'tags': tagString, 'ErrorScore' : error.errorweight }
        jsondata.append(dicerrordata);

        #print dicerrordata

    return jsondata



def mediapathrequest(request, path):
    return HttpResponseRedirect(STATIC_URL+path)


from urqa.models import Osstatistics

def filter_view(request,pid):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('filter.html')

    week, today = getTimeRange(TimeRange.weekly)

    try:
        projectElement = Projects.objects.get(apikey = pid)
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
            print os_idx
            osv_list.append({})
            osv_list[os_idx]['key'] = '%s.%s' % (v[0],v[1])
            osv_list[os_idx]['value'] = []
        osv_list[os_idx]['value'].append(e['osversion'])
    print 'yhc',osv_list

    appv_list = []
    app_idx = -1
    prev_v = ['-1','-1','-1']
    for e in valid_app:
        v = e['appversion'].split('.')
        if v[0] != prev_v[0] or v[1] != prev_v[1]:
            prev_v = v
            app_idx += 1
            print app_idx
            appv_list.append({})
            appv_list[app_idx]['key'] = '%s.%s' % (v[0],v[1])
            appv_list[app_idx]['value'] = []
        appv_list[app_idx]['value'].append(e['appversion'])
    print 'yhc',appv_list

    tag_list = []
    for e in valid_tag:
        tag_list.append(e['tag'])

    class_list = []
    for e in valid_class:
        class_list.append(e['errorclassname'])



    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'tag_list' : tag_list,
        'class_list' : class_list,
        'osv_list' : osv_list,
        'appv_list' : appv_list,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email,
        'profile_url' : user.image_path,
    });
    return HttpResponse(tpl.render(ctx))


def error_list(request,pid):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')
    try:
        projectElement = Projects.objects.get(apikey = pid)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse(json.dumps({"response":"fail"}), 'application/json');

    print request.POST
    jsonData = json.loads(request.POST['json'],encoding='utf-8')

    date = int(jsonData['date'])
    status = int(jsonData['status'])
    rank = jsonData['rank']

    week, today = getTimeRange(date)
    errorElements = Errors.objects.filter(pid=projectElement,rank__in=rank,status=status,lastdate__range=(week,today) ).order_by('-errorweight','rank', '-lastdate')
    print errorElements
    default = {"abc":'dfs'}
    return HttpResponse(json.dumps(default), 'application/json');