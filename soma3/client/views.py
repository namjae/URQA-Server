# Create your views here.
# -*- coding: utf-8 -*-


import os
import time
import json
import subprocess

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

from config import get_config

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
        errorElement.numofinstances += 1
        errorElement.totalmemusage += jsonData['appmemtotal']
        errorElement.wifion += int(jsonData['wifion']),
        errorElement.gpson += int(jsonData['gpson']),
        errorElement.mobileon += int(jsonData['mobileon']),
        errorElement.totalmemusage += int(jsonData['appmemtotal']),
        errorElement.save()

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
        Appstatistics.objects.create(iderror=errorElement,appversion=jsonData['appversion'],defaults={'count':1})
        Osstatistics.objects.create(iderror=errorElement,osversion=jsonData['osversion'],defaults={'count':1})
        Devicestatistics.objects.create(iderror=errorElement,devicename=jsonData['device'],defaults={'count':1})
        Countrystatistics.objects.create(iderror=errorElement,countryname=jsonData['country'],defaults={'count':1})
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
    log_path = os.path.join(get_config('log_pool_path'), '%s.txt' % str(idinstance))

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


@csrf_exempt
def receive_native(request):
    print 'receive_native requested'
    jsonData = json.loads(request.body,encoding='utf-8')


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
    if int(jsonData['rank']) == -1:
        autodetermine = 1 #True
    else:
        autodetermine = 0 #False

    errorElement = Errors(
        pid = projectElement,
        errorname = 'dummy',
        errorclassname = 'native',
        linenum = 0,
        autodetermine = autodetermine,
        rank = int(jsonData['rank']),
        #status = 0, # 0 = new, 1 = open, 2 = ignore, 3 = renew
        createdate = jsonData['datetime'],
        lastdate = jsonData['datetime'],
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
    dump_path = os.path.join(get_config('dmp_pool_path'), '%s.dmp' % str(idinstance))

    f = file(dump_path,'w')
    f.write(request.body)
    f.close()
    print 'log received : %s' % dump_path
    #step3: 저장한 로그파일을 db에 명시하기
    instanceElement.dump_path = dump_path
    instanceElement.save()

    #step4: dmp파일 분석
    sym_pool_path = os.path.join(get_config('sym_pool_path'),projectElement.pid)
    sym_pool_path = os.path.join(sym_pool_path, instanceElement.appversion)
    arg = [get_config('minidump_stackwalk_path') , dump_path, sym_pool_path]
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    #so library 추출
    ignore_clib = [
        'libdvm.so',
        'libc.so',
        'libcutils.so',
        'app_process',
        'libandroid_runtime.so',
        'libutils.so',
        'libbinder.so',
        'libjavacore.so',
    ]
    libs = []
    stderr_split = stderr.splitlines()
    for line in stderr_split:
        if line.find('Couldn\'t load symbols') == -1: #magic keyword
            continue
        lib = line[line.find('for: ')+5:].split('|')
        if lib[1] == '000000000000000000000000000000000' or lib[0] in ignore_clib:
            continue
        print lib[1] + ' ' + lib[0]
        libs.append(lib)




    #DB저장하기
    for lib in libs:
        sofileElement, created = Sofiles.objects.get_or_create(pid=projectElement, appversion=instanceElement.appversion, versionkey=lib[1], filename=lib[0],defaults={'uploaded':0})
        print created, ' ', sofileElement

    #print stdout
    cs_flag = 0
    stdout_split = stdout.splitlines()
    for line in stdout_split:
        if line.find('Crash reason:') != -1:
            errorname = line.split()[2]
        if line.find('Crash address:') != -1:
            errorclassname = line.split()[2]
        if line.find('(crashed)') != -1:
            callstack = line + '\n'
            cs_flag = cs_flag + 1
        elif cs_flag:
            if line.find('Thread') != -1 or cs_flag > 40:
                break;
            callstack += line + '\n'
            cs_flag = cs_flag + 1

    #print callstack

    try:
        errorElement_exist = Errors.objects.get(pid=projectElement, errorname=errorname, errorclassname=errorclassname)
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

        errorElement.delete()
        print 'native error %s:%s already exist' % (errorname, errorclassname)
    except ObjectDoesNotExist:
        errorElement.errorname = errorname
        errorElement.errorclassname = errorclassname
        errorElement.callstack = callstack
        errorElement.save()
        Appstatistics.objects.create(iderror=errorElement,appversion=instanceElement.appversion,defaults={'count':1})
        Osstatistics.objects.create(iderror=errorElement,osversion=instanceElement.osversion,defaults={'count':1})
        Devicestatistics.objects.create(iderror=errorElement,devicename=instanceElement.device,defaults={'count':1})
        Countrystatistics.objects.create(iderror=errorElement,countryname=instanceElement.country,defaults={'count':1})

    return HttpResponse('Success')