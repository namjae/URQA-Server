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
from django.db.models import Q

from common import validUserPjt
from common import getUserProfileDict
from common import getApikeyDict
from common import getSettingDict

from urqa.models import AuthUser
from urqa.models import Projects
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

from utility import getTemplatePath
from utility import getTimeRange
from utility import TimeRange
from utility import RANK
from utility import numbertostrcomma
from utility import get_dict_value_matchin_key
from utility import get_dict_value_matchin_number

from config import get_config


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
    stagecolordata = json.loads(get_config('app_stages_color'))

    name = request.POST['name']
    platformtxt = request.POST['platform']
    stagetxt = request.POST['stage']
    categorytxt = request.POST['category']


    platform = platformdata[platformtxt]
    stage =  stagedata[stagetxt]
    category= categorydata[categorytxt]
    color = stagecolordata[stagetxt]


    #project name은 중복을 허용한다.

    #step2: apikey를 발급받는다. apikeysms 8자리 숫자
    apikey = newApikey()
    print 'new apikey = %s' % apikey
    projectElement = Projects(owner_uid=userElement,apikey=apikey,name=name,platform=platform,stage=stage,category=category)
    projectElement.save();
    #step3: viwer db에 사용자와 프로젝트를 연결한다.
    Viewer.objects.create(uid=userElement,pid=projectElement)

    return HttpResponse(json.dumps({'success': True , 'prjname' : name , 'apikey' : apikey, 'color' : color , 'platform' : platformtxt}), 'application/json')

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
    sym_path = get_config('sym_pool_path') + '%s' % project.apikey
    if os.path.isdir(sym_path):
        shutil.rmtree(sym_path)
    so_path = get_config('so_pool_path') + '%s' % project.apikey
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

    #project modify
    projectelement.save();

    #timezone save
    userelement.timezone = request.POST['timezone']
    username.save();

    return HttpResponse(json.dumps({'success' : True , 'message' : 'success modify project'}),'application/json')

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

    sym_path = get_config('sym_pool_path') + '/%s' % projectElement.apikey
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

def so_upload(request, apikey):

    appver = request.POST['version']

    result, msg, userElement, projectElement = validUserPjt(request.user, apikey)

    #update_error_callstack(projectElement,appver)

    if not result:
        return HttpResponse(msg)

    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name

            so_path = get_config('so_pool_path') +'/%s' % apikey
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

def projects(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/urqa/')

    #주인인 project들
    UserElement = AuthUser.objects.get(username = request.user)
    OwnerProjectElements = Projects.objects.filter(owner_uid = UserElement.id)

    ViewerElements = Viewer.objects.filter(uid = UserElement.id).values('pid')
    ViewerProjectElements = Projects.objects.filter(pid__in = ViewerElements)

    MergeProjectElements = OwnerProjectElements | ViewerProjectElements

    #print MergeProjectElements

    project_list = []

    stagedata = json.loads(get_config('app_stages'))
    stagecolordata = json.loads(get_config('app_stages_color'))
    platformdata = json.loads(get_config('app_platforms'))

    for idx, project in enumerate(MergeProjectElements):
        projectdata = {}
        projectdata['apikey'] = project.apikey
        #stage color 구하기
        stagetxt = get_dict_value_matchin_key(stagedata,project.stage)
        projectdata['color'] = stagecolordata.get(stagetxt)

        Errorcounter = Errors.objects.filter(pid = project.pid).aggregate(Sum('numofinstances'))
        projectdata['errorcount'] =  Errorcounter['numofinstances__sum'] is not None and numbertostrcomma(Errorcounter['numofinstances__sum'])  or 0
        projectdata['name'] = project.name
        projectdata['platform'] = get_dict_value_matchin_key(platformdata,project.platform).lower()
        project_list.append(projectdata)

    categorydata = json.loads(get_config('app_categories'))
    platformdata = json.loads(get_config('app_platforms'))
    stagedata = json.loads(get_config('app_stages'))

    ctx = {
        'project_list' : project_list ,
        'app_platformlist' : platformdata.items(),
        'app_categorylist' : categorydata.items(),
        'app_stagelist' : stagedata.items()
    }
    return render(request, 'project-select.html', ctx)

def projectdashboard(request, apikey):

    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    print valid

    if not valid:
        return HttpResponseRedirect('/urqa')

    userdict = getUserProfileDict(userelement)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,userelement)

    dashboarddict = {
        'error_list' : errorscorelist(apikey),
    }

    ctx = dict(userdict.items() + apikeydict.items() + settingdict.items() + dashboarddict.items() )

    return render(request, 'projectdashboard.html', ctx)

def dailyesgraph(request, apikey):


    #기본 데이터
    default = {
	    "max":{"key":5, "value":0},
	    "tags":[
	        ]
        }

    #프로젝트 ID에 맞는 에러들을 가져오기 위함
    try:
        ProjectElement = Projects.objects.get(apikey= apikey)
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

def typeesgraph(request, apikey):

    timerange = TimeRange.weekly
    week , today = getTimeRange(timerange)


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
        print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json')


    for i in range(RANK.Unhandle,RANK.Native+1): # unhandled 부터 Native 까지
       ErrorsElements = Errors.objects.filter(pid = ProjectElement , lastdate__range = (week,today), rank = i) #일주일치 얻어옴
       if len(ErrorsElements) > 0:
           for error in ErrorsElements:
               default['tags'][i]['value'] += error.errorweight
               #print str(i) + ':' +  str(default['tags'][i]['value'])

    popcount = RANK.Unhandle
    for i in range(RANK.Unhandle,RANK.Native+1):
        if default['tags'][i - popcount]['value'] == 0:
            default['tags'].pop(i - popcount)
            popcount+=1

    result = json.dumps(default)


    return HttpResponse(result,'application/json')

def typeescolor(request ,apikey):

    timerange = TimeRange.weekly
    week , today = getTimeRange(timerange)


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
        print 'invalid pid'
        return HttpResponse(json.dumps(default), 'application/json')


    for i in range(RANK.Unhandle,RANK.Native+1): # unhandled 부터 Native 까지
       ErrorsElements = Errors.objects.filter(pid = ProjectElement , lastdate__range = (week,today), rank = i) #일주일치 얻어옴
       if len(ErrorsElements) > 0:
           for error in ErrorsElements:
               default['tags'][i]['value'] += error.errorweight
               #print str(i) + ':' +  str(default['tags'][i]['value'])

    ColorTable = []
    for i in range(RANK.Unhandle,RANK.Native+1):
        if default['tags'][i]['value'] != 0:
            ColorTable.append(RANK.rankcolorbit[i])

    result = json.dumps(ColorTable)
    return HttpResponse(result,'application/json')

#name, file, tag, counter
def errorscorelist(apikey):

    week, today = getTimeRange(TimeRange.weekly)

    try:
        ProjectElement = Projects.objects.get(apikey = apikey)
    except ObjectDoesNotExist:
        print 'invalid pid'
        return HttpResponse('')

    #print today

    ErrorElements = Errors.objects.filter(pid = ProjectElement , lastdate__range = (week, today) ).order_by('-errorweight','rank', '-lastdate')

    jsondata = [
    ]


    for error in ErrorElements:
        #if error.rank == RANK.Suspense:
            #continue
        TagElements = Tags.objects.filter(iderror = error)
        tagString = '';
        for tag in TagElements:
            tagString += tag.tag + ','
            # 마지막 , 제거
            if len(tagString) > 0:
                stringlength = len(tagString)
                tagString = tagString[0 : stringlength - 1]

        rankcolor = ''
        if error.rank == -1:
            rankcolor = 'none'
        else:
            rankcolor = RANK.rankcolor[error.rank]

        dicerrordata = {'ErrorName' : error.errorname ,
                        'ErrorClassName' : error.errorclassname + '(' + error.linenum + ')' ,
                        'tags': tagString,
                        'ErrorScore' : error.errorweight ,
                        'Errorid' : error.iderror ,
                        'Errorrankcolor' : rankcolor}
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