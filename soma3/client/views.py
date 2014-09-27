# Create your views here.
# -*- coding: utf-8 -*-


import os
import time
import json
import subprocess
import random
import sys

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
from urqa.models import Sofiles
from urqa.models import Appstatistics
from urqa.models import Osstatistics
from urqa.models import Devicestatistics
from urqa.models import Countrystatistics
from urqa.models import Activitystatistics
from urqa.models import Proguardmap

from utility import naive2aware
from utility import getUTCDatetime
from utility import getUTCawaredate
from utility import getUTCawaredatetime
from utility import RANK
from config import get_config
from soma3.settings import PROJECT_DIR

from common import validUserPjtError
from django.core.exceptions import MultipleObjectsReturned


#Client엡이 켜지면 이 루틴으로 접속이 들어오게된다.
#Client API를 입력받아 접속 통계
@csrf_exempt
def connect(request):
    #req_dump = request.copy();
    try:
        jsonData = json.loads(request.body,encoding='utf-8')
    except Exception as e:
        #Json Parsing Exception
        print >> sys.stderr, 'connect error!!!!! bad request.body'
        print >> sys.stderr, 'Exception = ', e
        return HttpResponse(json.dumps({'idsession':long(time.time() * 1000 + random.randint(0,1000))}), 'application/json');

    #step1: apikey를 이용하여 project찾기
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid from client(connect)'
        return HttpResponse(json.dumps({'idsession':'0'}), 'application/json');

    #step2: idsession 발급하기
    appversion = jsonData['appversion']
    idsession = long(time.time() * 1000 + random.randint(0,1000))

    print 'Project: %s, Ver: %s, new idsession: %d' % (projectElement.name,appversion,idsession)

    #step3: app version별 누적카운트 증가하기
    try:
        #App 실행횟수 증가
    	appruncountElement, created = Appruncount.objects.get_or_create(pid=projectElement,appversion=appversion,defaults={'runcount':1},date=getUTCawaredatetime())
    	if created == False:
        	appruncountElement.runcount += 1
        	appruncountElement.save()
    	else:
        	print 'project: %s, new version: %s' % (projectElement.name,appruncountElement.appversion)
    except MultipleObjectsReturned:
	print "MultipleObjectsReturned in client app version count"

    return HttpResponse(json.dumps({'idsession':idsession}), 'application/json');


def client_data_validate(jsonData):
    #Client에서 비정상 데이터가 올라오는 경우가 발생하여 방어 코드를 넣었음.
    oriData = jsonData.copy();
    errorFlag = 0
    if not 'apikey' in jsonData:
        jsonData['apikey'] = 'unknown'
        errorFlag = 1
    if not 'errorname' in jsonData:
        jsonData['errorname'] = 'unknown'
        errorFlag = 1
    if len(jsonData['errorname']) >= 499:
        jsonData['errorname'] = jsonData['errorname'][0:499]
        errorFlag = 1
    if not 'errorclassname' in jsonData:
        jsonData['errorclassname'] = 'unknown'
        errorFlag = 1
    if len(jsonData['errorclassname']) >= 299:
        jsonData['errorclassname'] = jsonData['errorclassname'][0:299]
        errorFlag = 1
    if not 'linenum' in jsonData:
        jsonData['linenum'] = 'unknown'
        errorFlag = 1
    if not 'callstack' in jsonData:
        jsonData['callstack'] = 'unknown'
        errorFlag = 1
    if not 'wifion' in jsonData:
        jsonData['wifion'] = 0
        errorFlag = 1
    if not 'gpson' in jsonData:
        jsonData['gpson'] = 0
        errorFlag = 1
    if not 'mobileon' in jsonData:
        jsonData['mobileon'] = 0
        errorFlag = 1
    if not 'appversion' in jsonData:
        jsonData['appversion'] = 'unknown'
        errorFlag = 1
    if not 'osversion' in jsonData:
        jsonData['osversion'] = 'unknown'
        errorFlag = 1
    if not 'device' in jsonData:
        jsonData['device'] = 'unknown'
        errorFlag = 1
    if not 'country' in jsonData:
        jsonData['country'] = 'unknown'
        errorFlag = 1
    if not 'lastactivity' in jsonData:
        jsonData['lastactivity'] = 'unknown'
        errorFlag = 1
    if not 'rank' in jsonData:
        jsonData['rank'] = RANK.Critical
        errorFlag = 1
    if int(jsonData['rank']) < 0 or int(jsonData['rank']) > 4:
        jsonData['rank'] = RANK.Critical
        errorFlag = 1
    if not 'sdkversion' in jsonData:
        jsonData['sdkversion'] = 'unknown'
        errorFlag = 1
    if not 'kernelversion' in jsonData:
        jsonData['kernelversion'] = 'unknown'
        errorFlag = 1
    if not 'appmemmax' in jsonData:
        jsonData['appmemmax'] = 'unknown'
        errorFlag = 1
    if not 'appmemfree' in jsonData:
        jsonData['appmemfree'] = 'unknown'
        errorFlag = 1
    if not 'appmemtotal' in jsonData:
        jsonData['appmemtotal'] = 'unknown'
        errorFlag = 1
    if not 'locale' in jsonData:
        jsonData['locale'] = 'unknown'
        errorFlag = 1
    if not 'rooted' in jsonData:
        jsonData['rooted'] = 0
        errorFlag = 1
    if not 'scrheight' in jsonData:
        jsonData['scrheight'] = 0
        errorFlag = 1
    if not 'scrwidth' in jsonData:
        jsonData['scrwidth'] = 0
        errorFlag = 1
    if not 'scrorientation' in jsonData:
        jsonData['scrorientation'] = 0
        errorFlag = 1
    if not 'sysmemlow' in jsonData:
        jsonData['sysmemlow'] = 'unknown'
        errorFlag = 1
    if not 'batterylevel' in jsonData:
        jsonData['batterylevel'] = 0
        errorFlag = 1
    if not 'availsdcard' in jsonData:
        jsonData['availsdcard'] = 0
        errorFlag = 1
    if not 'xdpi' in jsonData:
        jsonData['xdpi'] = 0
        errorFlag = 1
    if not 'ydpi' in jsonData:
        jsonData['ydpi'] = 0
        errorFlag = 1
    if not 'eventpaths' in jsonData:
        jsonData['eventpaths'] = 'unknown'
        errorFlag = 1

    #Error가 발생하면 어떤데이터에서 에러가 발생했는지 확인하기위해 로그 찍기
    if errorFlag == 1:
        print >> sys.stderr, 'exception Data Error: ', oriData
        print >> sys.stderr, 'Revise JSON Data    : ', jsonData

    return jsonData

def proguard_retrace_oneline(string,linenum,map_path,mapElement):
    #Proguard에서 한줄만 파싱하기위한 루틴
    #Proguard Line parsing
    if mapElement == None:
        return string
    for i in range(1,100):
        temp_path = os.path.join(map_path,'temp'+str(i)+'.txt')
        if not os.path.isfile(temp_path):
            break
    fp = open(temp_path , 'wb')
    fp.write('at\t'+string+'\t(:%s)' % linenum)
    fp.close()

    #Config.cfg파일로부터 Proguard위치를 파악하여 라인 Parsing
    arg = ['java','-jar',os.path.join(PROJECT_DIR,get_config('proguard_retrace_path')),'-verbose',os.path.join(map_path,mapElement.filename),temp_path]

    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()
    stdout_split = stdout.split('\t')
    string = stdout_split[1]

    os.remove(temp_path)
    return string

def proguard_retrace_callstack(string,map_path,mapElement):
    #Callstack전체를 Parsing해주는 루틴.
    if mapElement == None:
        return string
    for i in range(1,100):
        temp_path = os.path.join(map_path,'temp'+str(i)+'.txt')
        if not os.path.isfile(temp_path):
            break
    fp = open(temp_path , 'wb')
    fp.write(string)
    fp.close()

    arg = ['java','-jar',os.path.join(PROJECT_DIR,get_config('proguard_retrace_path')),'-verbose',os.path.join(map_path,mapElement.filename),temp_path]
    #print arg
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()
    string = stdout

    os.remove(temp_path)
    return string

@csrf_exempt
def receive_exception(request):
    #Client로부터 올라오는 exception을 수집하는 루틴
    try:
        jsonData = json.loads(request.body,encoding='utf-8')
        #req_dump = None
    except Exception as e:
        print >> sys.stderr, 'connect error!!!!! bad request.body'
        #print >> sys.stderr, 'request.body = ', req_dump.body
        #print >> sys.stderr, 'request = ',req_dump
        print >> sys.stderr, 'Exception = ', e
        #req_dump = None
        return HttpResponse(json.dumps({'idinstance':0}), 'application/json');

    #Client로부터 들어온 데이터의 무결성을 검사한다.
    jsonData = client_data_validate(jsonData)


    #step1: apikey를 이용하여 project찾기
    #apikey가 validate한지 확인하기.
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid apikey'
        return HttpResponse('Invalid apikey')

    #Exception데이터 로깅.
    print >> sys.stderr, 'receive_exception requested',apikey
    print >> sys.stderr, '=========== JsonData ========='
    print >> sys.stderr, jsonData
    print >> sys.stderr, '=============================='

    #step2: errorname, errorclassname, linenum을 이용하여 동일한 에러가 있는지 찾기
    errorname = jsonData['errorname']
    errorclassname = jsonData['errorclassname']
    linenum = jsonData['linenum']

    print >> sys.stderr, 'appver:', jsonData['appversion'], 'osver:', jsonData['osversion']
    print >> sys.stderr, '%s %s %s' % (errorname,errorclassname,linenum)

    #step2-0: Proguard 적용 확인
    appversion = jsonData['appversion']

    map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
    map_path = os.path.join(map_path,projectElement.apikey)
    map_path = os.path.join(map_path,appversion)
    try:
        #Proguard가 적용된 프로젝트의 경우 Proguard Map파일을 이용하여 Parsing한다.
        mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion)

        errorname = proguard_retrace_oneline(errorname,linenum,map_path,mapElement)
        errorclassname = proguard_retrace_oneline(errorclassname,linenum,map_path,mapElement)
        callstack = proguard_retrace_callstack(jsonData['callstack'],map_path,mapElement)
    except ObjectDoesNotExist:
        #Proguard가 적용되지 않은 프로젝트의 경우 데이터를 그대로 사용함.
        mapElement = None
        callstack = jsonData['callstack']
        print 'no proguard mapfile'

    try:
        #동일 에러가 있는지 DB로부터 얻어온다.
        #동일 에러가 없을경우 exception루틴으로 간다.

        errorElement = Errors.objects.get(pid=projectElement,errorname=errorname,errorclassname=errorclassname,linenum=linenum)

        #새로온 인스턴스 정보로 시간 갱신
        #errorElement.lastdate = naive2aware(jsonData['datetime'])
        errorElement.callstack = callstack
        errorElement.lastdate = getUTCawaredatetime()
        errorElement.numofinstances += 1
        #errorElement.totalmemusage += jsonData['appmemtotal']
        errorElement.wifion += int(jsonData['wifion'])
        errorElement.gpson += int(jsonData['gpson'])
        errorElement.mobileon += int(jsonData['mobileon'])
        errorElement.totalmemusage += int(jsonData['appmemtotal'])
        errorElement.save()

        #통계에 사용할 DB갱신
        e, created = Appstatistics.objects.get_or_create(iderror=errorElement,appversion=jsonData['appversion'],defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Osstatistics.objects.get_or_create(iderror=errorElement,osversion=jsonData['osversion'],defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Devicestatistics.objects.get_or_create(iderror=errorElement,devicename=jsonData['device'],defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Countrystatistics.objects.get_or_create(iderror=errorElement,countryname=jsonData['country'],defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Activitystatistics.objects.get_or_create(iderror=errorElement,activityname=jsonData['lastactivity'],defaults={'count':1})
        if not created:
            e.count += 1
            e.save()

    except ObjectDoesNotExist:
        #새로운 에러로 판별하여 DB 에러테이블에 데이터를 생성한다.
        autodetermine = 0 #deprecated
        errorElement = Errors(
            pid = projectElement,
            errorname = errorname,
            errorclassname = errorclassname,
            linenum = linenum,
            autodetermine = autodetermine,
            rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
            status = 0, # 0 = new, 1 = open, 2 = fixed, 3 = ignore
            createdate = getUTCawaredatetime(),
            lastdate = getUTCawaredatetime(),
            numofinstances = 1,
            callstack = callstack,
            wifion = jsonData['wifion'],
            gpson = jsonData['gpson'],
            mobileon = jsonData['mobileon'],
            totalmemusage = jsonData['appmemtotal'],
            errorweight = 10,
            recur = 0,
        )
        errorElement.save()
        #통계용 데이터도 생성한다.
        Appstatistics.objects.create(iderror=errorElement,appversion=jsonData['appversion'],count=1)
        Osstatistics.objects.create(iderror=errorElement,osversion=jsonData['osversion'],count=1)
        Devicestatistics.objects.create(iderror=errorElement,devicename=jsonData['device'],count=1)
        Countrystatistics.objects.create(iderror=errorElement,countryname=jsonData['country'],count=1)
        Activitystatistics.objects.create(iderror=errorElement,activityname=jsonData['lastactivity'],count=1)
        #error score 계산 에러스코어 삭제
        #calc_errorScore(errorElement)
    #step3: 테그 저장
    if jsonData['tag']:
        #테그 데이터가 있다면 테그를 생성한다.
        tagstr = jsonData['tag']
        tagElement, created = Tags.objects.get_or_create(iderror=errorElement,pid=projectElement,tag=tagstr)


    #step4: 인스턴스 생성하기
    #1개의 에러에는 여러개이 인스턴스
    instanceElement = Instances(
        iderror = errorElement,
        ins_count = errorElement.numofinstances,
        sdkversion = jsonData['sdkversion'],
        appversion = jsonData['appversion'],
        osversion = jsonData['osversion'],
        kernelversion = jsonData['kernelversion'],
        appmemmax = jsonData['appmemmax'],
        appmemfree = jsonData['appmemfree'],
        appmemtotal = jsonData['appmemtotal'],
        country = jsonData['country'],
        datetime = getUTCawaredatetime(),
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
        ydpi = jsonData['ydpi'],
        lastactivity = jsonData['lastactivity'],
        callstack = callstack,
    )
    # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
    instanceElement.save()


    #step5: 이벤트패스 생성
    #print 'here! ' + instanceElement.idinstance
    #instanceElement.update()
    print >> sys.stderr, 'instanceElement.idinstance',instanceElement.idinstance
    eventpath = jsonData['eventpaths']

    depth = 10
    for event in reversed(eventpath):
        temp_str = event['classname'] + '.' + event['methodname']
        temp_str = proguard_retrace_oneline(temp_str,event['linenum'],map_path,mapElement)
        flag = temp_str.rfind('.')
        classname = temp_str[0:flag]
        methodname =  temp_str[flag+1:]
        if not 'label' in event:    #event path에 label적용, 기존버전과 호환성을 확보하기위해 'label'초기화를 해줌 client ver 0.91 ->
            event['label'] = ""
        Eventpaths.objects.create(
            idinstance = instanceElement,
            iderror = errorElement,
            ins_count = errorElement.numofinstances,
            datetime = naive2aware(event['datetime']),
            classname = classname,
            methodname = methodname,
            linenum = event['linenum'],
            label = event['label'],
            depth = depth
        )
        depth -= 1

    #calc_eventpath(errorElement)
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
    log_path = os.path.join(PROJECT_DIR,os.path.join(get_config('log_pool_path'), '%s.txt' % str(idinstance)))

    f = file(log_path,'w')
    f.write(request.body)
    f.close()

    print 'log received : %s' % log_path
    #step3: 저장한 로그파일을 db에 명시하기
    instanceElement.log_path = log_path
    instanceElement.save()

    return HttpResponse('success')

@csrf_exempt
def receive_eventpath(request):
    #print request.body
    jsonData = json.loads(request.body,encoding='utf-8')
    #print jsonData
    idsession = jsonData['idsession']
    eventpath = jsonData['eventpaths']

    session_key = Session.objects.get(idsession=idsession)
    for event in eventpath:
        Sessionevent.objects.create(idsession=session_key,
                                    datetime=naive2aware(event['datetime']),
                                    classname=event['classname'],
                                    methodname=event['methodname'],
                                    linenum=event['linenum'])

    return HttpResponse('success')


@csrf_exempt
def receive_native(request):
    #Client Native를 받는 루틴
    print 'receive_native requested'
    try:
        jsonData = json.loads(request.body,encoding='utf-8')
        #req_dump = None
    except Exception as e:
        print >> sys.stderr, 'connect error!!!!! bad request.body'
        #print >> sys.stderr, 'request.body = ', req_dump.body
        #print >> sys.stderr, 'request = ',req_dump
        print >> sys.stderr, 'Exception = ', e
        #req_dump = None
        return HttpResponse(json.dumps({'idinstance':0}), 'application/json');
    #print jsonData

    jsonData = client_data_validate(jsonData)

    #step1: apikey를 이용하여 project찾기
    #apikey가 validate한지 확인하기.
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid apikey'
        return HttpResponse('Invalid apikey')


    #step2: dummy errorElement생성
    #새로 들어온 에러라면 새로운 에러 생성
    #if int(jsonData['rank']) == -1:
    #    autodetermine = 1 #True
    #else:
    #    autodetermine = 0 #False
    autodetermine = 0

    errorElement = Errors(
        pid = projectElement,
        errorname = 'dummy',
        errorclassname = 'native',
        linenum = 0,
        autodetermine = autodetermine,
        rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
        status = 0, # 0 = new, 1 = open, 2 = ignore, 3 = renew
        createdate = getUTCawaredatetime(),
        lastdate = getUTCawaredatetime(),
        numofinstances = 1,
        callstack = '',#jsonData['callstack'],
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
        tagElement, created = Tags.objects.get_or_create(iderror=errorElement,pid=projectElement,tag=tagstr)
    #step4: 인스턴스 생성하기

    instanceElement = Instances(
        iderror = errorElement,
        ins_count = errorElement.numofinstances,
        sdkversion = jsonData['sdkversion'],
        appversion = jsonData['appversion'],
        osversion = jsonData['osversion'],
        kernelversion = jsonData['kernelversion'],
        appmemmax = jsonData['appmemmax'],
        appmemfree = jsonData['appmemfree'],
        appmemtotal = jsonData['appmemtotal'],
        country = jsonData['country'],
        datetime = getUTCawaredatetime(),
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
        ydpi = jsonData['ydpi'],
        lastactivity = jsonData['lastactivity'],
    )
    # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
    instanceElement.save()


    #step5: 이벤트패스 생성
    #print 'here! ' + instanceElement.idinstance
    #instanceElement.update()
    appversion = jsonData['appversion']

    map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
    map_path = os.path.join(map_path,projectElement.apikey)
    map_path = os.path.join(map_path,appversion)

    try:
        mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion)
    except ObjectDoesNotExist:
        mapElement = None
        print 'no proguard mapfile'



    print 'instanceElement.idinstance',instanceElement.idinstance
    eventpath = jsonData['eventpaths']

    depth = 10
    for event in reversed(eventpath):
        temp_str = event['classname'] + '.' + event['methodname']
        temp_str = proguard_retrace_oneline(temp_str,event['linenum'],map_path,mapElement)
        flag = temp_str.rfind('.')
        classname = temp_str[0:flag]
        methodname =  temp_str[flag+1:]

        if not 'label' in event:    #event path에 label적용, 기존버전과 호환성을 확보하기위해 'label'초기화를 해줌 client ver 0.91 ->
            event['label'] = ""
        Eventpaths.objects.create(
            idinstance = instanceElement,
            iderror = errorElement,
            ins_count = errorElement.numofinstances,
            datetime = naive2aware(event['datetime']),
            classname = classname,
            methodname = methodname,
            linenum = event['linenum'],
            label = event['label'],
            depth = depth,
        )
        depth -= 1
    return HttpResponse(json.dumps({'idinstance':instanceElement.idinstance}), 'application/json');

#Native Symbol중에 Android 기본 Symbol은 제외함.
class Ignore_clib:
    list = [
        'libWVStreamControlAPI_L1',
        'libwebviewchromium',
        'libLLVM.so',
        'libdvm.so',
        'libc.so',
        'libcutils.so',
        'app_process',
        'libandroid_runtime.so',
        'libutils.so',
        'libbinder.so',
        'libjavacore.so',
        'librs_jni.so',
        'linker',
        'eglsubAndroid.so'
    ]


@csrf_exempt
def receive_native_dump(request, idinstance):
    #step1: idinstance에 해당하는 인스턴스 구하기
    try:
        instanceElement = Instances.objects.get(idinstance=int(idinstance))
        errorElement = instanceElement.iderror
        projectElement = errorElement.pid
        #이미 로그가 저장되었다면 다음으로 들어오는 로그는 버그 또는 외부공격으로 생각하고 차단
        if instanceElement.dump_path:
            return HttpResponse('Already exists')
    except ObjectDoesNotExist:
        print 'Invalid idinstance %d' % int(idinstance)
        return HttpResponse('Fail')

    #step2: dump파일 저장하기
    dump_path = os.path.join(PROJECT_DIR,os.path.join(get_config('dmp_pool_path'), '%s.dmp' % str(idinstance)))

    f = file(dump_path,'w')
    f.write(request.body)
    f.close()
    print 'log received : %s' % dump_path
    #step3: 저장한 로그파일을 db에 명시하기
    instanceElement.dump_path = dump_path
    instanceElement.save()

    #step4: dmp파일 분석(with nosym)
    arg = [os.path.join(PROJECT_DIR,get_config('minidump_stackwalk_path')) , dump_path]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    #so library 추출
    libs = []
    stderr_split = stderr.splitlines()
    for line in stderr_split:
        if line.find('Couldn\'t load symbols') == -1: #magic keyword
            continue
        lib = line[line.find('for: ')+5:].split('|')
        if lib[1] == '000000000000000000000000000000000' or lib[0] in Ignore_clib.list:
            continue
        #print lib[1] + ' ' + lib[0]
        libs.append(lib)




    #DB저장하기
    for lib in libs:
        sofileElement, created = Sofiles.objects.get_or_create(pid=projectElement, appversion=instanceElement.appversion, versionkey=lib[1], filename=lib[0],defaults={'uploaded':'X'})
        if created:
            print 'new version key : ', lib[1], lib[0]
        else:
            print 'version key:', lib[1], lib[0], 'already exists'

    #ErrorName, ErrorClassname, linenum 추출하기
    cs_flag = 0
    errorname = ''
    errorclassname = ''
    linenum = ''
    stdout_split = stdout.splitlines()
    for line in stdout_split:
        if line.find('Crash reason:') != -1:
            errorname = line.split()[2]
        if cs_flag:
            if line.find('Thread') != -1 or errorclassname:
                break
            #errorclassname 찾기
            for lib in libs:
                flag = line.find(lib[0])
                if flag == -1:
                    continue
                separator = line.find(' + ')
                if separator != -1:
                    errorclassname = line[flag:separator]
                    linenum = line[separator+3:]
                else:
                    errorclassname = line[flag:]
                    linenum = 0
                break
        if line.find('(crashed)') != -1:
            cs_flag = 1

    #dmp파일 분석(with sym)
    sym_pool_path = os.path.join(PROJECT_DIR,os.path.join(get_config('sym_pool_path'),str(projectElement.apikey)))
    sym_pool_path = os.path.join(sym_pool_path, instanceElement.appversion)
    arg = [os.path.join(PROJECT_DIR,get_config('minidump_stackwalk_path')) , dump_path, sym_pool_path]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    cs_count = 0
    callstack = ''
    stdout_split = stdout.splitlines()
    for line in stdout_split:
        if line.find('(crashed)') != -1:
            callstack = line
            cs_count = cs_count + 1
        elif cs_count:
            if line.find('Thread') != -1 or cs_count > 40:
                break;
            callstack += '\n'
            callstack += line
            cs_count = cs_count + 1

    #print callstack

    try:
        errorElement_exist = Errors.objects.get(pid=projectElement, errorname=errorname, errorclassname=errorclassname, linenum=linenum)
        errorElement_exist.lastdate = errorElement.lastdate
        errorElement_exist.numofinstances += 1
        errorElement_exist.wifion += errorElement.wifion
        errorElement_exist.gpson += errorElement.gpson
        errorElement_exist.mobileon += errorElement.mobileon
        errorElement_exist.totalmemusage += errorElement.totalmemusage
        errorElement_exist.save()
        instanceElement.iderror = errorElement_exist
        instanceElement.save()

        e, created = Appstatistics.objects.get_or_create(iderror=errorElement,appversion=instanceElement.appversion,defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Osstatistics.objects.get_or_create(iderror=errorElement,osversion=instanceElement.osversion,defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Devicestatistics.objects.get_or_create(iderror=errorElement,devicename=instanceElement.device,defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Countrystatistics.objects.get_or_create(iderror=errorElement,countryname=instanceElement.country,defaults={'count':1})
        if not created:
            e.count += 1
            e.save()
        e, created = Activitystatistics.objects.get_or_create(iderror=errorElement,activityname=instanceElement.lastactivity,defaults={'count':1})
        if not created:
            e.count += 1
            e.save()



        errorElement.delete()
        #errorscore 계산  에러스코어삭제
        #calc_errorScore(errorElement_exist)
        print 'native error %s:%s already exist' % (errorname, errorclassname)
    except ObjectDoesNotExist:
        errorElement.errorname = errorname
        errorElement.errorclassname = errorclassname
        errorElement.callstack = callstack
        errorElement.linenum = linenum
        errorElement.save()
        Appstatistics.objects.create(iderror=errorElement,appversion=instanceElement.appversion,count=1)
        Osstatistics.objects.create(iderror=errorElement,osversion=instanceElement.osversion,count=1)
        Devicestatistics.objects.create(iderror=errorElement,devicename=instanceElement.device,count=1)
        Countrystatistics.objects.create(iderror=errorElement,countryname=instanceElement.country,count=1)
        Activitystatistics.objects.create(iderror=errorElement,activityname=instanceElement.lastactivity,count=1)
        #errorscore 계산 에러스코어 삭제
        #calc_errorScore(errorElement)
    return HttpResponse('Success')
