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
from urqa.models import Activitystatistics
from urqa.models import Proguardmap

from utility import naive2aware
from utility import getUTCDatetime
from utility import getUTCawaredate
from utility import RANK
from config import get_config
from soma3.settings import PROJECT_DIR

#삭제요망
from common import validUserPjtError



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
    duple = Session.objects.filter(idsession=idsession);
    if len(duple) != 0:
        idsession = long(time.time() * 1000 + 1);
    Session.objects.create(idsession=idsession,pid=projectElement,appversion=appversion)
    print 'Project: %s, Ver: %s, new idsession: %d' % (projectElement.name,appversion,idsession)

    #step3: app version별 누적카운트 증가하기
    appruncountElement, created = Appruncount.objects.get_or_create(pid=projectElement,appversion=appversion,defaults={'runcount':1},date=getUTCawaredate())
    if created == False:
        appruncountElement.runcount += 1
        appruncountElement.save()
    else:
        print 'project: %s, new version: %s' % (projectElement.name,appruncountElement.appversion)
    return HttpResponse(json.dumps({'idsession':idsession}), 'application/json');

def proguard_retrace_oneline(string,linenum,map_path,mapElement):
    if mapElement == None:
        return string
    for i in range(1,100):
        temp_path = os.path.join(map_path,'temp'+str(i)+'.txt')
        if not os.path.isfile(temp_path):
            break
    fp = open(temp_path , 'wb')
    fp.write('at\t'+string+'\t(:%s)' % linenum)
    fp.close()

    arg = ['java','-jar',os.path.join(PROJECT_DIR,get_config('proguard_retrace_path')),'-verbose',os.path.join(map_path,mapElement.filename),temp_path]
    #print arg
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()
    stdout_split = stdout.split('\t')
    string = stdout_split[1]

    os.remove(temp_path)
    return string

def proguard_retrace_callstack(string,map_path,mapElement):
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

    #step2-0: Proguard 적용 확인
    appversion = jsonData['appversion']

    map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
    map_path = os.path.join(map_path,projectElement.apikey)
    map_path = os.path.join(map_path,appversion)
    try:
        mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion)

        errorname = proguard_retrace_oneline(errorname,linenum,map_path,mapElement)
        errorclassname = proguard_retrace_oneline(errorclassname,linenum,map_path,mapElement)
        callstack = proguard_retrace_callstack(jsonData['callstack'],map_path,mapElement)
    except ObjectDoesNotExist:
        mapElement = None
        callstack = jsonData['callstack']
        print 'no proguard mapfile'

    try:
        errorElement = Errors.objects.get(pid=projectElement,errorname=errorname,errorclassname=errorclassname,linenum=linenum)
        #새로온 인스턴스 정보로 시간 갱신

        errorElement.lastdate = naive2aware(jsonData['datetime'])
        errorElement.numofinstances += 1
        #errorElement.totalmemusage += jsonData['appmemtotal']
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

        #에러 스코어 계산 에러스코어 삭제
        #calc_errorScore(errorElement)

    except ObjectDoesNotExist:
        #RANK 값이 이상하게 들어오면 Unhandle로 변경
        if int(jsonData['rank']) < 0 or int(jsonData['rank']) > 4:
            jsonData['rank'] = RANK.Unhandle
        #새로 들어온 에러라면 새로운 에러 생성
        #if int(jsonData['rank']) == -1:
        #    autodetermine = 1 #True
        #else:
        #    autodetermine = 0 #False
        autodetermine = 0

        errorElement = Errors(
            pid = projectElement,
            errorname = errorname,
            errorclassname = errorclassname,
            linenum = linenum,
            autodetermine = autodetermine,
            rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
            status = 0, # 0 = new, 1 = open, 2 = fixed, 3 = ignore
            createdate = naive2aware(jsonData['datetime']),
            lastdate = naive2aware(jsonData['datetime']),
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
        Appstatistics.objects.create(iderror=errorElement,appversion=jsonData['appversion'],count=1)
        Osstatistics.objects.create(iderror=errorElement,osversion=jsonData['osversion'],count=1)
        Devicestatistics.objects.create(iderror=errorElement,devicename=jsonData['device'],count=1)
        Countrystatistics.objects.create(iderror=errorElement,countryname=jsonData['country'],count=1)
        Activitystatistics.objects.create(iderror=errorElement,activityname=jsonData['lastactivity'],count=1)
        #error score 계산 에러스코어 삭제
        #calc_errorScore(errorElement)
    #step3: 테그 저장
    if jsonData['tag']:
        tagstr = jsonData['tag']
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
        callstack = callstack,
    )
    # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
    instanceElement.save()


    #step5: 이벤트패스 생성
    #print 'here! ' + instanceElement.idinstance
    #instanceElement.update()
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
    #RANK 값이 이상하게 들어오면 Unhandle로 변경
    if int(jsonData['rank']) < 0 or int(jsonData['rank']) > 4:
        jsonData['rank'] = RANK.Unhandle
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
    appversion = jsonData['appversion']

    map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
    map_path = os.path.join(map_path,projectElement.apikey)
    map_path = os.path.join(map_path,appversion)
    mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion)

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


class Ignore_clib:
    list = [
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

def calc_errorScore(errorElement):

    erscore_parameter = json.loads(get_config('error_score_parameter'))

    date_er_score = 0.0
    quantity_er_score = 0.0
    rank_er_score = 0.0

    #date 계산 k1
    #print naive2aware(getUTCDatetime())
    #print errorElement.lastdate
    d = naive2aware(getUTCDatetime()) - errorElement.lastdate

    #print d
    #print d.days, d.seconds, d.microseconds
    #print erscore_parameter['retention']
    #print float(erscore_parameter['retention'])

    date_er_score = ((erscore_parameter['retention'])/ (erscore_parameter['retention'] + float(d.days) )) * erscore_parameter['date_constant']
    #print 'bunmo : '+ str((erscore_parameter['retention'] + d.days))
    #print 'daily delta : ' +str(d.days)
    #print 'bunja: ' + str(erscore_parameter['retention'])
    #print 'date cal : ' + str(date_er_score)


    #quantity 계산 k2
    runcounts = Appruncount.objects.filter(pid=errorElement.pid)     #전체 앱버전별 실행수
    errorcounts = Appstatistics.objects.filter(iderror=errorElement) #1개 에러에 대한 앱버전별 실행수

    tlb = []
    for r in runcounts:
        for e in errorcounts:
            if r.appversion == e.appversion:
                tlb.append({'appversion':r.appversion,'runcount':r.runcount,'errcount':e.count})
                break;

        #print 'calc_errorscore',tlb

    wholeErrorCounter = 0.0
    errorCounter = 0.0
    for version_statics in tlb:
        wholeErrorCounter += version_statics['runcount']
        errorCounter += version_statics['errcount']

    quantity_er_score = errorCounter/wholeErrorCounter
    #print 'whole : ' + str(wholeErrorCounter)
    #print 'errorcount : ' + str(errorCounter)
    #print 'quantity cal : ' + str(quantity_er_score)

    #rank 계산 k3
    rank_er_score = 0
    rank_er_score = rank_to_constant(errorElement.rank) * erscore_parameter['rank_ratio_constant']
    #print 'RANK : ' + RANK.toString[errorElement.rank]
    #print 'rank cal : ' + str(rank_er_score)

    #최종 ErrorScore 계산
    error_Score = (date_er_score + quantity_er_score + rank_er_score) * erscore_parameter['constant']
    #print 'last Error Score : ' + str(error_Score)

    #디비에 저장
    errorElement.errorweight = error_Score
    errorElement.gain1 = float(date_er_score)
    errorElement.gain2 = float(quantity_er_score)

    errorElement.save()

def rank_to_constant(int):

    erscore_parameter = json.loads(get_config('error_score_parameter'))

    if int == RANK.Native:
        return erscore_parameter['na']
    elif int == RANK.Unhandle:
        return erscore_parameter['un']
    elif int == RANK.Critical:
        return erscore_parameter['cr']
    elif int == RANK.Major:
        return erscore_parameter['ma']
    elif int == RANK.Minor:
        return erscore_parameter['mi']
    else:
        return 'fail'
