# Create your views here.
# -*- coding: utf-8 -*-

import json
import operator
import datetime
import sys
from django.db.models import Count
from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from distutils.version import LooseVersion, StrictVersion

from common import validUserPjt
from common import getUserProfileDict
from common import getApikeyDict
from common import getSettingDict

from utility import getTimeRange
from utility import getTimeRangeExactHour
from utility import Status
from utility import getTimezoneMidNight
from utility import getTimezoneHour

from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Instances
from urqa.models import ErrorsbyApp
from urqa.models import SessionbyApp
from urqa.models import CountrysbyApp
from urqa.models import Erbd
from urqa.models import Erba
from urqa.models import ErbvApps
from urqa.models import Erbv
from urqa.models import TotalSession

# 임시로 포함함 --> 나중에 없애 거나, urqa.models 로 옮길 예정 
from django.db import models

def statistics(request,apikey):
    #통계페이지를 Randering하는 루틴
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('statistics.html')

    #userdict = getUserProfileDict(userelement)
    userdict = getUserProfileDict(user)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,userelement)

    
    statisticsdict = {
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
    }

    ctxdict = dict(userdict.items() + apikeydict.items() + settingdict.items() + statisticsdict.items() )
    ctx = Context(ctxdict)

    #return render(request, 'statistics.html', ctx)
    return HttpResponse(tpl.render(ctx))


def chartdata_sbav(request,apikey):
    #App version별 Client의 Session을 보여주는 차트
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    #print 'retention', retention

    if retention == 1:
        retention = 24 #retention을 24로 변경 24시를 의미
        past, today = getTimeRangeExactHour(retention,projectElement.timezone)
        strformat = '%y-%m-%d %H'
        dateformat = '%%y-%%m-%%d %%H'
    else:
        past, today = getTimeRange(retention,projectElement.timezone)
        strformat = '%y-%m-%d'
        dateformat = '%%y-%%m-%%d'
    #########################################
    #90% 에 해당하는 appversion 리스트 얻어오는 로직
    # 1. 전체 session 수 구하기
    # 2. 전체 세션수 대비 90% 에 해당하는 app version 리스트만 가져옴
    #########################################
    sql2 = 'SELECT appversion ,sum(appruncount) as total FROM appruncount2 where pid = %(pidinput)s and datetime >= %(pasttime)s group by appversion order by total desc'
    params2 = {'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}
    totalSession = TotalSession.objects.raw(sql2, params2)
    sum = 0
    for idx, pl in enumerate(totalSession):
        sum = sum + pl.total
    ratio = float(sum) / 1.1

    ratioappversion = ()
    ratioappversion = list(ratioappversion)

    sum = 0
    recentVersion = '0.0'
    othersNumber = 0 
    for idx, pl in enumerate(totalSession):
        if len(ratioappversion) == 0:
            ratioappversion.append(str(pl.appversion))
        sum = sum + pl.total
        if LooseVersion(recentVersion) < LooseVersion(pl.appversion):
            if not pl.appversion == "unknown":
                recentVersion = pl.appversion
        if sum < ratio:
            ratioappversion.append(str(pl.appversion))
        else:
            othersNumber = othersNumber + pl.total

    #check recent version is exist in array
    if not recentVersion in ratioappversion:
        ratioappversion.append(str(recentVersion))

    ratioappversion = tuple(ratioappversion)

    if len(ratioappversion) == 1:
        ratioappversion =  str(ratioappversion)[:len(str(ratioappversion)) - 2] + str(ratioappversion)[-1]

    #날짜별 Session수를 얻어오기 위한 Query생성
    sql = 'SELECT idappruncount2 as idsessionbyapp, sum(appruncount) as runcount, appversion, DATE_FORMAT(CONVERT_TZ(datetime,"UTC",%(timezone)s),"' + dateformat +'") as sessionday'
    sql = sql + ' from urqa.appruncount2'
    if len(ratioappversion) == 0:
        sql = sql + ' where pid = %(pidinput)s and datetime >= %(pasttime)s and appversion'
    else:
        sql = sql + ' where pid = %(pidinput)s and datetime >= %(pasttime)s and appversion in ' + str(ratioappversion)
    sql = sql + ' Group by appversion, sessionday'
    params = {'timezone':projectElement.timezone,'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}
    places = SessionbyApp.objects.raw(sql, params)

    appversions = []
    dates = []
    for idx, pl in enumerate(places):
        if not pl.appversion in appversions:
            appversions.append(pl.appversion)
        if not pl.sessionday in dates:
            dates.append(pl.sessionday)

    result = {}

    categories = []
    appcount_data = {}
    for appversion in appversions:
        appcount_data[appversion] = []

    new_places = []
    for idx, pl in enumerate(places):
        new_places.append({'appversion':pl.appversion,'sessionday':pl.sessionday,'runcount':pl.runcount})

    #시간,날짜별로 Session Data를 나눔

    for i in range(retention-1,-1,-1):
        if retention == 24: # Statistics 하루치
            day1 = getTimezoneHour(projectElement.timezone) + datetime.timedelta(hours =  -i)
            if day1.hour == 0:
                categories.append(day1.strftime('%b-%d'))
            else:
                categories.append(day1.strftime('%H'))
        else:
            day1 = getTimezoneMidNight(projectElement.timezone) + datetime.timedelta(days =  -i)
            categories.append(day1.strftime('%b-%d'))
        for appversion in appversions:
            result_runcount = 0
            for idx in range(0,len(new_places)):
                if new_places[idx]['appversion'] == appversion and new_places[idx]['sessionday'] == day1.strftime(strformat):
                    result_runcount = new_places[idx]['runcount']
                    new_places.pop(idx)
                    break
            appcount_data[appversion].append(int(result_runcount))

    appver_data = []
    for appversion in appversions:
        appver_data.append(
            {
                'name': appversion,
                'data': appcount_data[appversion]
            }
        )
    chart_sbav = {'categories':categories,'data':appver_data}
    result['chart_sbav'] = chart_sbav

    return HttpResponse(json.dumps(result), 'application/json');

def chartdata_ebav(request,apikey):
    #App version별 Client의 Error 수를 보여주는 차트
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    # Common Data
    result = {}

    #appcount_data = {}
    categories = []
    #appver_data = []

    if retention == 1:
        retention = 24 #retention을 24로 변경 24시를 의미
        past, today = getTimeRangeExactHour(retention,projectElement.timezone)
        strformat = '%y-%m-%d %H'
        dateformat = '%%y-%%m-%%d %%H'
    else:
        past, today = getTimeRange(retention,projectElement.timezone)
        strformat = '%y-%m-%d'
        dateformat = '%%y-%%m-%%d'

    #########################################
    #90% 에 해당하는 appversion 리스트 얻어오는 로직
    # 1. 전체 session 수 구하기
    # 2. 전체 세션수 대비 90% 에 해당하는 app version 리스트만 가져옴
    #########################################
    #sql2 = 'SELECT appversion ,count(*) as total FROM instances A, errors B where A.iderror = B.iderror and pid = %(pidinput)s and B.status in (0,1)  and datetime >= %(pasttime)s group by appversion order by total desc'
    sql2 =  "SELECT appversion ,count(*) as total "
    sql2 = sql2 + "FROM instances "
    sql2 = sql2 + "where pid =  %(pidinput)s and datetime >= %(pasttime)s "
    sql2 = sql2 + "group by appversion "
    sql2 = sql2 + "order by total desc"


    params2 = {'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}


    totalSession = TotalSession.objects.raw(sql2, params2)

    #======= 장고로 변환 테스트가 안되어 있음;;
    # pasttime= '%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)
    #
    # totalSession = sorted(Instances.objects.values('appversion').annotate(total=Count('*')).filter(
    #     pid=projectElement, datetime__gte=pasttime
    # ).group_by('appversion'), key=lambda instance: instance['total'], reverse=True)

    sum = 0
    for idx, pl in enumerate(totalSession):
        sum = sum + pl.total
    ratio = float(sum) / 1.1

    ratioappversion = ()
    ratioappversion = list(ratioappversion)

    sum = 0
    recentVersion = '0.0'
    othersNumber = 0 
    for idx, pl in enumerate(totalSession):
        if len(ratioappversion) == 0:
            ratioappversion.append(str(pl.appversion))
        sum = sum + pl.total
        if LooseVersion(recentVersion) < LooseVersion(pl.appversion):
            if not pl.appversion == "unknown":
                recentVersion = pl.appversion
        if sum < ratio:
                ratioappversion.append(str(pl.appversion))
        else:
            othersNumber = othersNumber + pl.total
    #check recent version is exist in array
    if not recentVersion in ratioappversion:
        ratioappversion.append(str(recentVersion))

    ratioappversion = tuple(ratioappversion)

    if len(ratioappversion) == 1:
        ratioappversion =  str(ratioappversion)[:len(str(ratioappversion)) - 2] + str(ratioappversion)[-1]



    #Error Count를 얻어올 Query를 생성한다.
    sql = "select count(*) as errorcount ,appversion, DATE_FORMAT(CONVERT_TZ(datetime,'UTC',%(timezone)s),'" + dateformat + "') as errorday "
    sql = sql + "from instances "
    sql = sql + "where pid = %(pidinput)s "
    if len(ratioappversion) == 0:
        sql = sql + ' and datetime >= %(pasttime)s and appversion '
    else:
        sql = sql + ' and datetime >= %(pasttime)s and appversion in ' + str(ratioappversion)
    sql = sql + "group by errorday,appversion"

    past, today = getTimeRange(retention,projectElement.timezone)

    params = {'timezone':projectElement.timezone,'pidinput':projectElement.pid,'pasttime':'%d-%d-%d %d:%d:%d' % (past.year,past.month,past.day,past.hour,past.minute,past.second)}
    places = ErrorsbyApp.objects.raw(sql, params)
    
    #listing app version
    appversions = []
    dates = []
    for idx, pl in enumerate(places):
        if not pl.appversion in appversions:
            appversions.append(pl.appversion)
        if not pl.errorday in dates:
            dates.append(pl.errorday)

    result = {}

    categories = []
    appcount_data = {}
    for appversion in appversions:
        appcount_data[appversion] = []

    new_places = []
    for idx, pl in enumerate(places):
        new_places.append({'appversion':pl.appversion,'errorday':pl.errorday,'errorcount':pl.errorcount})

    #시간,날짜별로 Error Count를 나눔
    for i in range(retention-1,-1,-1):
        if retention == 24:
            day1 = getTimezoneHour(projectElement.timezone) + datetime.timedelta(hours =  -i)
            if day1.hour == 0:
                categories.append(day1.strftime('%b-%d'))
            else:
                categories.append(day1.strftime('%H'))
        else:
            day1 = getTimezoneMidNight(projectElement.timezone) + datetime.timedelta(days =  -i)
            categories.append(day1.strftime('%b-%d'))
        for appversion in appversions:
            result_runcount = 0
            for idx in range(0,len(new_places)):
                if new_places[idx]['appversion'] == appversion and new_places[idx]['errorday'] == day1.strftime(strformat):
                    result_runcount = new_places[idx]['errorcount']
                    new_places.pop(idx)
                    break
            appcount_data[appversion].append(int(result_runcount))

    appver_data = []
    for appversion in appversions:
        appver_data.append(
            {
                'name': appversion,
                'data': appcount_data[appversion]
            }
        )
    chart_ebav = {'categories':categories,'data':appver_data}
    result['chart_sbav'] = chart_ebav


    chart1 = {'categories':categories,'data':appver_data}
    result['chart1'] = chart1
    #print >>sys.stderr, chart1
    return HttpResponse(json.dumps(result), 'application/json');

class Erbc(models.Model):
    errorclassname = models.CharField(primary_key=True, max_length=300)
    count = models.IntegerField(blank=True, null=True)

def chartdata_erbc(request,apikey):
    #발생한 에러를 Class별로 나누어 나타낸다.
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])
    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    # Common Data
    #past, today = getTimeRange(retention,projectElement.timezone)

    sql = "select errorclassname, ( select count(*) from instances where iderror = A.iderror ) as cnt "
    sql = sql + "from errors A "
    sql = sql + "where lastdate > (curdate() - interval %(intervalinput)s day) and A.pid = %(pidinput)s "

    params = {'pidinput':projectElement.pid,'intervalinput':retention }

    tmp = Erbc.objects.raw(sql, params)
    chart2 = []

    for idx, pl in enumerate(tmp):
        chart2.append( [str(pl.errorclassname), int(pl.cnt) ] )
        #print str(pl.errorclassname)

    result = {}
    result['chart2'] = chart2
    return HttpResponse(json.dumps(result), 'application/json');

def chartdata_erbd(request,apikey):
    #발생한 에러를 Device별로 나누어 나타낸다.
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')
    
    # 하루치 통계
    if retention == 1:
        sql = 'select device, count(*) as sum from instances where pid = %(pidinput)s and datetime BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() group by device'

    else:
    #하루 이상인 경우
        sql = 'SELECT A.device, A.sum FROM( '
        sql = sql + 'SELECT DEVICE, SUM(SUMCOUNT) as SUM FROM ERBD WHERE PID = %(pidinput)s AND COUNTEDAT BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() '
        sql = sql + 'group by DEVICE ) A'
        sql = sql + ' order by sum desc limit 12'

    # query run
    params = {'pidinput':projectElement.pid,'retentioninput':retention}
    places = Erbd.objects.raw(sql, params)

    categories = []
    temp_data = []
    for idx, pl in enumerate(places):
        categories.append(str(pl.device))
        temp_data.append(int(pl.sum))

    dev_data = [{'name':'Device','data':temp_data}]
    chart3 = {'categories':categories,'data':dev_data}
    result = {}
    result['chart3'] = chart3

    return HttpResponse(json.dumps(result), 'application/json');

def chartdata_erba(request,apikey):
    #발생한 에러를 Activity별로 나누어 나타낸다.
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    result = {}
    # 하루치 통계
    if retention == 1:
        sql = 'select LASTACTIVITY as activity, count(*) as sum from instances where pid = %(pidinput)s and datetime BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() group by lastactivity'

    else:
    #하루 이상인 경우
        sql = 'SELECT A.LASTACTIVITY as activity, A.sum FROM( '
        sql = sql + 'SELECT LASTACTIVITY, SUM(SUMCOUNT) as SUM FROM ERBA WHERE PID = %(pidinput)s AND COUNTEDAT BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() AND lastactivity > ""'
        sql = sql + 'group by LASTACTIVITY ) A'
        sql = sql + ' order by sum desc limit 12'


    categories = []
    temp_data = []
    params = {'pidinput':projectElement.pid,'retentioninput':retention}
    places = Erba.objects.raw(sql, params)

    for idx, pl in enumerate(places):
        categories.append(str(pl.activity))
        temp_data.append(int(pl.sum))

    act_data = [{'name':'Device','data':temp_data}]
    chart4 = {'categories':categories,'data':act_data}
    result['chart4'] = chart4

    return HttpResponse(json.dumps(result), 'application/json');


def chartdata_erbv(request,apikey):
    #발생한 에러를 OSVersion / AppVersion 별로 나누어 나타낸다.
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    result = {}
    categories = []
    osversions = []
    ver_data = []
    osversions2 = []
    temp_data = []

    # 하루치 통계
    if retention == 1:
        sql2 =          'select appversion, osversion, count(*) as sum from instances where pid = %(pidinput)s and datetime BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() '
        sql2 = sql2 +   'group by appversion, osversion '
        sql2 = sql2 +   'order by appversion desc, osversion desc' 

    else:
        #하루 이상인 경우
        #max 12개만 가져올 appversion 구하는 쿼리
        sql = 'SELECT appversion, sum FROM ( '
        sql = sql + 'SELECT sum(sumcount) as sum, appversion from ERBV where pid = %(pidinput)s and COUNTEDAT BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() '
        sql = sql + 'group by appversion ) A '
        sql = sql + 'order by sum desc limit 12'
        params = {'pidinput':projectElement.pid,'retentioninput':retention}
        places = ErbvApps.objects.raw(sql, params)

        arrayInput = ()
        arrayInput = list(arrayInput)
        for idx, pl in enumerate(places):
                arrayInput.append(str(pl.appversion))

        arrayInput = tuple(arrayInput)
        if len(arrayInput) == 1:
            arrayInput =  str(arrayInput)[:len(str(arrayInput)) - 2] + str(arrayInput)[-1]
        sql2 = 'SELECT A.appversion , A.osversion, A.sum FROM( '
        if len(arrayInput) == 0:
            sql2 = sql2 + 'SELECT appversion, osversion, SUM(SUMCOUNT) as SUM FROM ERBV WHERE PID = %(pidinput)s AND COUNTEDAT BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW()  '
        else:
            sql2 = sql2 + 'SELECT appversion, osversion, SUM(SUMCOUNT) as SUM FROM ERBV WHERE PID = %(pidinput)s AND COUNTEDAT BETWEEN DATE_SUB(NOW(), INTERVAL %(retentioninput)s DAY) AND NOW() AND appversion in  ' + str(arrayInput)
        sql2 = sql2 + ' group by appversion, osversion ) A '
        sql2 = sql2 + ' order by appversion desc, osversion desc'

    # raw query run and make data 
    params2 = {'pidinput':projectElement.pid,'retentioninput':retention}
    places2 = Erbv.objects.raw(sql2, params2)
     #fill categories
    for idx, pl in enumerate(places2):
        if pl.appversion not in categories:
            categories.append(str(pl.appversion))

    for idx, pl in enumerate(places2):
        if pl.osversion not in osversions:
            osversions.append(str(pl.osversion))

    matrix = [[0 for i in range(len(categories))] for j in range(len(osversions))]
    for idx, pl in enumerate(places2):
        #get appversion's index
        index1 = categories.index(pl.appversion)
        index2 = osversions.index(pl.osversion)
        matrix[index2][index1] = int(pl.sum)

    mindex = 0
    for idx, pl in enumerate(places2):
        if pl.osversion not in osversions2:
            osversions2.append(str(pl.osversion))
            ver_data.append({'name':pl.osversion,'data':matrix[mindex]})
            mindex = mindex + 1

    chart5 = {'categories':categories,'data':ver_data}
    result['chart5'] = chart5

    return HttpResponse(json.dumps(result), 'application/json');

def chartdata_ebcs(request,apikey):
    #발생한 에러를 Country(나라)별로 나누어 나타낸다.
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    # Common Data
    result = {}

    #chart4
    temp_data = {}
    activities = []

    sql = "select count(*) count, country from instances "
    sql = sql + " where pid = %(pname)s "
    sql = sql + " and datetime > (curdate() - interval %(intervalinput)s day) "
    sql = sql + " group by country"
    sql = sql + " order by count desc"
    sql = sql + " limit 10"

    params = {'pname':projectElement.pid, 'intervalinput':retention }
    counts = CountrysbyApp.objects.raw(sql, params)

    categories = []
    temp_data = []

    for idx, pl in enumerate(counts):
        categories.append(pl.country)
        temp_data.append(pl.count)


    act_data = [{'name':'Country','data':temp_data}]
    chart6 = {'categories':categories,'data':act_data}
    result['chart6'] = chart6
    return HttpResponse(json.dumps(result), 'application/json');

