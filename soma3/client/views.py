# Create your views here.
# -*- coding: utf-8 -*-

import time
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from client.models import Session
from client.models import Sessionevent
from client.models import Projects
from client.models import Errors
from client.models import Instances
@csrf_exempt
def connect(request):
    idsession = long(time.time() * 1000000)
    jsonData = json.loads(request.body,encoding='utf-8')
    sessionElement = Session(idsession=idsession,apikey=jsonData['apikey'],appversion=jsonData['appversion'])

    sessionElement.save()
    return HttpResponse(json.dumps({'idsession':idsession}), 'application/json');

@csrf_exempt
def receive_exception(request):
    jsonData = json.loads(request.body,encoding='utf-8')

    #step1: apikey를 이용하여 project찾기
    #apikey가 validate한지 확인하기.
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print "Invalid apikey"
        return HttpResponse('Invalid apikey')


    #step2: errorname, errorclassname, linenum을 이용하여 동일한 에러가 있는지 찾기
    errorname = jsonData['errorname']
    errorclassname = jsonData['errorclassname']
    linenum = jsonData['linenum']

    try:
        errorElement = Errors.objects.get(pid=projectElement,errorname=errorname,errorclassname=errorclassname,linenum=linenum)
    except ObjectDoesNotExist:
        #새로 들어온 에러라면 새로운 에러 생성
        if int(jsonData['rank']) == -1:
            autodetermine = 1 #True
        else:
            autodetermine = 0 #False

        errorElement = Errors.objects.create(
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


    #step3: 인스턴스 생성하기

    instanceElement = Instances.objects.create(
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
        mobileon = jsonData['mobaileon'],
        gpson = jsonData['gpson'],
        wifion = jsonData['wifion'],
        device = jsonData['device'],
        rooted = jsonData['rooted'],
        scrheight = jsonData['scrheight'],
        scrwidth = jsonData['scrwidth'],
        scrorientation = jsonData['scr'],
        sysmemlow = jsonData['sysmemlow'],
        #eventpath = ,
        #log_path = ,
        betterylevel = jsonData['betterylevel'],
        availsdcard = jsonData['availsdcard'],
        xdpi = jsonData['xdpi'],
        ydpi = jsonData['ydpi']
    )

    #step4: 이벤트패스 생성



    return HttpResponse('test')

@csrf_exempt
def receive_exception_log(request, idinstance):

    return HttpResponse('test');

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

    return HttpResponse('done')