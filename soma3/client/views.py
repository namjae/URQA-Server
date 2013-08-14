# Create your views here.
# -*- coding: utf-8 -*-

import os
import time
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from urqa.models import Session
from urqa.models import Sessionevent
from urqa.models import Projects
from urqa.models import Errors
from urqa.models import Instances
from urqa.models import Eventpaths
from urqa.models import Tags
from urqa.models import Appruncount

@csrf_exempt
def connect(request):
    jsonData = json.loads(request.body,encoding='utf-8')

    #step1: apikey를 이용하여 project찾기
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid from client(connect)'
        return HttpResponse(json.dumps({'idsession':'0'}), 'application/json');

    #step2: idsession 발급하기
    appversion = jsonData['appversion']
    idsession = long(time.time() * 1000000)
    Session.objects.create(idsession=idsession,pid=projectElement,appversion=appversion)
    print 'new idsession: %d' % idsession

    #step3: app version별 누적카운트 증가하기
    appruncountElement, created = Appruncount.objects.get_or_create(pid=projectElement,appversion=appversion,defaults={'runcount':1})
    if created == False:
        appruncountElement.runcount += 1
        appruncountElement.save()
    else:
        print 'project: %s, new version: %s' % (projectElement.name,appruncountElement.appversion)
    return HttpResponse(json.dumps({'idsession':idsession}), 'application/json');

@csrf_exempt
def receive_exception(request):
    jsonData = json.loads(request.body,encoding='utf-8')

    print 'receive_exception requested'
    #step1: apikey를 이용하여 project찾기
    #apikey가 validate한지 확인하기.
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid apikey'
        return HttpResponse('Invalid apikey')


    #step2: errorname, errorclassname, linenum을 이용하여 동일한 에러가 있는지 찾기
    errorname = jsonData['errorname']
    errorclassname = jsonData['errorclassname']
    linenum = jsonData['linenum']

    print '%s %s %s' % (errorname,errorclassname,linenum)

    try:
        errorElement = Errors.objects.get(pid=projectElement,errorname=errorname,errorclassname=errorclassname,linenum=linenum)
        #새로온 인스턴스 정보로 시간 갱신
        errorElement.lastdate = jsonData['datetime']
        errorElement.totalmemusage += jsonData['appmemtotal']
        errorElement.save()
    except ObjectDoesNotExist:
        #새로 들어온 에러라면 새로운 에러 생성
        if int(jsonData['rank']) == -1:
            autodetermine = 1 #True
        else:
            autodetermine = 0 #False

        errorElement = Errors(
            pid = projectElement,
            errorname = errorname,
            errorclassname = errorclassname,
            linenum = linenum,
            autodetermine = autodetermine,
            rank = int(jsonData['rank']),
            status = 0, # 0 = new, 1 = open, 2 = ignore, 3 = renew
            createdate = jsonData['datetime'],
            lastdate = jsonData['datetime'],
            numofinstances = 1,
            callstack = jsonData['callstack'],
            wifion = jsonData['wifion'],
            gpson = jsonData['gpson'],
            mobileon = jsonData['mobileon'],
            totalmemusage = jsonData['appmemtotal'],
            errorweight = 10,
            recur = 0,
        )
        errorElement.save()

    #step3: 테그 저장
    tagstr = jsonData['tag']
    if tagstr:
        tagElement, created = Tags.object.get_or_create(iderror=errorElement,tag=tagstr)

    #step4: 인스턴스 생성하기

    instanceElement = Instances(
        iderror = errorElement,
        sdkversion = jsonData['sdkversion'],
        appversion = jsonData['appversion'],
        osversion = jsonData['osversion'],
        kernelversion = jsonData['kernelversion'],
        appmemmax = jsonData['appmemmax'],
        appmemfree = jsonData['appmemfree'],
        appmemtotal = jsonData['appmemtotal'],
        country = jsonData['country'],
        datetime = jsonData['datetime'],
        locale = jsonData['locale'],
        mobileon = jsonData['mobileon'],
        gpson = jsonData['gpson'],
        wifion = jsonData['wifion'],
        device = jsonData['device'],
        rooted = jsonData['rooted'],
        scrheight = jsonData['scrheight'],
        scrwidth = jsonData['scrwidth'],
        scrorientation = jsonData['scrorientation'],
        sysmemlow = jsonData['sysmemlow'],
        log_path = '',
        batterylevel = jsonData['batterylevel'],
        availsdcard = jsonData['availsdcard'],
        xdpi = jsonData['xdpi'],
        ydpi = jsonData['ydpi']
    )
    # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
    instanceElement.save()


    #step5: 이벤트패스 생성
    #print 'here! ' + instanceElement.idinstance
    #instanceElement.update()
    print instanceElement.idinstance
    eventpath = jsonData['eventpaths']

    for event in eventpath:
        Eventpaths.objects.create(
            idinstance = instanceElement,
            datetime = event['datetime'],
            classname = event['classname'],
            methodname = event['methodname'],
            linenum = int(event['linenum'])
        )


    return HttpResponse(json.dumps({'idinstance':instanceElement.idinstance}), 'application/json');

@csrf_exempt
def receive_exception_log(request, idinstance):

    #step1: idinstance에 해당하는 인스턴스 구하기
    try:
        instanceElement = Instances.objects.get(idinstance=int(idinstance))
        #이미 로그가 저장되었다면 다음으로 들어오는 로그는 버그? 또는 외부공격으로 생각하고 차단
        if instanceElement.log_path:
            return HttpResponse('Already exists')
    except ObjectDoesNotExist:
        print 'Invalid idinstance %d' % int(idinstance)
        return HttpResponse('Fail')

    #step2: log파일 저장하기
    log_path = os.path.join('/urqa/logpool', '%s.txt' % str(idinstance))

    f = file(log_path,'w')
    f.write(request.body)
    f.close()

    #step3: 저장한 로그파일을 db에 명시하기
    instanceElement.log_path = log_path
    instanceElement.save()

    return HttpResponse('success')

@csrf_exempt
def receive_eventpath(request):

    jsonData = json.loads(request.body,encoding='utf-8')
    print jsonData
    idsession = long(jsonData['idsession'])
    eventpath = jsonData['eventpaths']

    session_key = Session.objects.get(idsession = idsession)
    for event in eventpath:
        Sessionevent.objects.create(idsession = session_key,
                                    datetime = event['datetime'],
                                    classname = event['classname'],
                                    methodname = event['methodname'],
                                    linenum = int(event['linenum']))

    return HttpResponse('success')