# Create your views here.
# -*- coding: utf-8 -*-


import os
import time
import json
import subprocess
import datetime

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
from utility import naive2aware

from config import get_config

@csrf_exempt
def connect(request):
    jsonData = json.loads(request.body,encoding='utf-8')
    #print jsonData

    #step1: apikey를 이용하여 project찾기
    try:
        apikey = jsonData['apikey']
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Invalid from client(connect)'
        return HttpResponse(json.dumps({'idsession':'0'}), 'application/json');

    #step2: idsession 발급하기
    appversion = jsonData['appversion']
    idsession = long(time.time() * 1000)
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

        errorElement.lastdate = naive2aware(jsonData['datetime'])
        errorElement.numofinstances += 1
        errorElement.totalmemusage += jsonData['appmemtotal']
        errorElement.wifion += int(jsonData['wifion'])
        errorElement.gpson += int(jsonData['gpson'])
        errorElement.mobileon += int(jsonData['mobileon'])
        errorElement.totalmemusage += int(jsonData['appmemtotal'])
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
        e, created = Activitystatistics.objects.get_or_create(iderror=errorElement,activityname=jsonData['lastactivity'],defaults={'count':1})
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
            rank = int(jsonData['rank']), # unhandled = 0, native = 1, critical = 2, major = 3, minor = 4
            status = 0, # 0 = new, 1 = open, 2 = fixed, 3 = ignore
            createdate = naive2aware(jsonData['datetime']),
            lastdate = naive2aware(jsonData['datetime']),
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
        Appstatistics.objects.create(iderror=errorElement,appversion=jsonData['appversion'],count=1)
        Osstatistics.objects.create(iderror=errorElement,osversion=jsonData['osversion'],count=1)
        Devicestatistics.objects.create(iderror=errorElement,devicename=jsonData['device'],count=1)
        Countrystatistics.objects.create(iderror=errorElement,countryname=jsonData['country'],count=1)
        Activitystatistics.objects.create(iderror=errorElement,activityname=jsonData['lastactivity'],count=1)
    #step3: 테그 저장
    if jsonData['tag']:
        tagstr = jsonData['tag']
        tagElement, created = Tags.objects.get_or_create(iderror=errorElement,tag=tagstr)

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
        datetime = naive2aware(jsonData['datetime']),
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
    print instanceElement.idinstance
    eventpath = jsonData['eventpaths']

    #테스트때문에 잠시 안씀
    depth = 1
    for event in eventpath:
        Eventpaths.objects.create(
            idinstance = instanceElement,
            iderror = errorElement,
            ins_count = errorElement.numofinstances,
            datetime = naive2aware(event['datetime']),
            classname = event['classname'],
            methodname = event['methodname'],
            linenum = int(event['linenum']),
            depth = depth
        )
        depth += 1

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
                                    linenum=int(event['linenum']))

    return HttpResponse('success')


@csrf_exempt
def receive_native(request):
    print 'receive_native requested'
    #print request.body
    jsonData = json.loads(request.body,encoding='utf-8')
    #print jsonData

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
        createdate = naive2aware(jsonData['datetime']),
        lastdate = naive2aware(jsonData['datetime']),
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
        ins_count = errorElement.numofinstances,
        sdkversion = jsonData['sdkversion'],
        appversion = jsonData['appversion'],
        osversion = jsonData['osversion'],
        kernelversion = jsonData['kernelversion'],
        appmemmax = jsonData['appmemmax'],
        appmemfree = jsonData['appmemfree'],
        appmemtotal = jsonData['appmemtotal'],
        country = jsonData['country'],
        datetime = naive2aware(jsonData['datetime']),
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

    depth = 1
    for event in eventpath:
        Eventpaths.objects.create(
            idinstance = instanceElement,
            iderror = errorElement,
            ins_count = errorElement.numofinstances,
            datetime = naive2aware(event['datetime']),
            classname = event['classname'],
            methodname = event['methodname'],
            linenum = int(event['linenum']),
            depth = depth,
        )
        depth += 1


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
    sym_pool_path = os.path.join(get_config('sym_pool_path'),str(projectElement.pid))
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
        #print lib[1] + ' ' + lib[0]
        libs.append(lib)




    #DB저장하기
    for lib in libs:
        sofileElement, created = Sofiles.objects.get_or_create(pid=projectElement, appversion=instanceElement.appversion, versionkey=lib[1], filename=lib[0],defaults={'uploaded':0})
        if created:
            print 'new version key : ', lib[1], lib[0]
        else:
            print 'version key:', lib[1], lib[0], 'already exists'

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
        e, created = Activitystatistics.objects.get_or_create(iderror=errorElement,activityname=instanceElement.lastactivity,defaults={'count':1})
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
        Appstatistics.objects.create(iderror=errorElement,appversion=instanceElement.appversion,count=1)
        Osstatistics.objects.create(iderror=errorElement,osversion=instanceElement.osversion,count=1)
        Devicestatistics.objects.create(iderror=errorElement,devicename=instanceElement.device,count=1)
        Countrystatistics.objects.create(iderror=errorElement,countryname=instanceElement.country,count=1)
        Activitystatistics.objects.create(iderror=errorElement,activityname=instanceElement.lastactivity,count=1)
    return HttpResponse('Success')

def calc_eventpath(errorElement):


    #node들 추출하기
#    eventHashs = []
    instance_limit_count = 10 #최근 몇개의 Instance의 이벤트패스만 표시할지 결정
    depth_max = 10 # event path 최대 깊이
    depth_count = 6 # Depth몇개 표현할지 정함


    ins_count_limit = max(1, errorElement.numofinstances - instance_limit_count)

    id_count = 0
    k2i_table = {}
    i2k_table = {}
    link_table = {}

    depth = 10
    while depth > (depth_max - depth_count):
        eventHash = {}
        #최근 인스턴스를 우선적으로 비교하기위해 -idinstance를 사용함
        eventElements = Eventpaths.objects.filter(iderror=errorElement,depth=depth,ins_count__gt=ins_count_limit).order_by('-idinstance')
        limit_count = 0
        for event in eventElements:
            key = str(depth) + ':' + event.classname + ':' + event.methodname + ':' + str(event.linenum)
            #key = str(depth) + ':' + str(event.linenum)
            if not key in eventHash:
                eventHash[key] = 1
            else:
                eventHash[key] += 1
            limit_count += 1
            if limit_count == instance_limit_count:
                break;
        sorted_list = sorted(eventHash, key=eventHash.get, reverse=True)

        #이벤트가 5개를 초과하면 5번째를 Others로 변경함
        other_count = 0
        if len(sorted_list) > 5:
            while len(sorted_list) > 4:
                key = sorted_list[4]
                other_count += eventHash[key]
                del(eventHash[key])
                sorted_list.pop(4)
            eventHash[str(depth) + ':' + 'Others'] = other_count
            sorted_list.append(str(depth) + ':' + 'Others')
        #print sorted_list
        #print len(sorted_list)

        #id 발급하기
        for key in sorted_list:
            k2i_table[key] = id_count
            i2k_table[id_count] = key
            id_count += 1

        depth -= 1

    #test라서 idinstance__lte=159쿼리를 날림
    #instanceElements = Instances.objects.filter(iderror=errorElement,idinstance__lte=159).order_by('-idinstance')
    instanceElements = Instances.objects.filter(iderror=errorElement,ins_count__gt=ins_count_limit).order_by('-idinstance')

    limit_count = 0
    for instanceElement in instanceElements:
        #print instanceElement.idinstance
        eventElements = Eventpaths.objects.filter(iderror=errorElement,idinstance=instanceElement).order_by('-depth')

        length = len(eventElements)
        for i in range(0,depth_count-1):
            #print i
            source_key = str(eventElements[i].depth) + ':' + eventElements[i].classname + ':' + eventElements[i].methodname + ':' + str(eventElements[i].linenum)
            #source_key = str(eventElements[i].depth) + ':' + str(eventElements[i].linenum)
            if not source_key in k2i_table:
                source_id = k2i_table[str(eventElements[i].depth) + ':' + 'Others']
            else:
                source_id = k2i_table[source_key]
            target_key = str(eventElements[i+1].depth) + ':' + eventElements[i+1].classname + ':' + eventElements[i+1].methodname + ':' + str(eventElements[i+1].linenum)
            #target_key = str(eventElements[i+1].depth) + ':' + str(eventElements[i+1].linenum)
            if not target_key in k2i_table:
                target_id = k2i_table[str(eventElements[i].depth) + ':' + 'Others']
            else:
                target_id = k2i_table[target_key]

            link_key = '%d>%d' % (source_id, target_id)
            if link_key in link_table:
                link_table[link_key] += 1
            else:
                link_table[link_key] = 1
            #print source_key, target_key, source_id, target_id

        limit_count += 1
        if limit_count == instance_limit_count:
            break

    #print i2k_table
    #print link_table

    result = {}
    result['nodes'] = []
    for id in i2k_table:
        result['nodes'].append({'name':i2k_table[id]})
    result['links'] = []
    for link in link_table:
        key = link.split('>')
        sid = int(key[0])
        tid = int(key[1])
        result['links'].append({'source':sid,'target':tid,'value':link_table[link]})
    print json.dumps(result)
    return result