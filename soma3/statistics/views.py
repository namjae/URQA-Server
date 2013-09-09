# Create your views here.
# -*- coding: utf-8 -*-

import json

from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from common import validUserPjt
from common import getUserProfileDict
from common import getApikeyDict
from common import getSettingDict

from utility import getTimeRange
from utility import TimeRange
from utility import Status

from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Devicestatistics
from urqa.models import Instances
from urqa.models import Projects


def statistics(request,apikey):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,apikey)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('statistics.html')

    userdict = getUserProfileDict(userelement)
    apikeydict = getApikeyDict(apikey)
    settingdict = getSettingDict(projectelement,userelement)

    statisticsdict = {
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
    }

    ctxdict = dict(userdict.items() + apikeydict.items() + settingdict.items() + statisticsdict.items() )
    ctx = Context(ctxdict)
    return HttpResponse(tpl.render(ctx))



def chartdata(request,apikey):
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = int(jsonData['retention'])

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,apikey)
    if not valid:
        return HttpResponseRedirect('/urqa')

    past, today = getTimeRange(retention)
    errorElements = Errors.objects.filter(pid=projectElement,status__in=[Status.New,Status.Open,Status.Renew],lastdate__range=(past,today)).order_by('errorclassname','errorweight')

    #Chart1
    chart1 = []
    pre_class = ''
    for e in errorElements:
        if pre_class != e.errorclassname:
            pre_class = e.errorclassname
            chart1.append([e.errorclassname, e.errorweight])
        else:
            last = len(chart1)
            chart1[last-1] = [e.errorclassname,chart1[last-1][1] + (e.errorweight)]


    result = {}
    result['chart1'] = chart1

    #Chart2
    chart2 = []
    temp_data = {}
    for e in errorElements:
        devices = Devicestatistics.objects.filter(iderror=e).order_by('devicename')
        if devices.count() == 0:
            continue
        total = 0
        for d in devices:
            total += d.count
            #print d.devicename
        #print total,e.errorweight

        for d in devices:
            if not d.devicename in temp_data:
                temp_data[d.devicename] = e.errorweight * d.count / total
            else:
                temp_data[d.devicename] += e.errorweight * d.count / total
    for e in temp_data:
        chart2.append({
            'label': e,
            'value': temp_data[e],
        })

    result['chart2'] = chart2

    #Chart4
    categories = []
    ver_data = []
    temp_data = {}
    instances = Instances.objects.select_related().filter(iderror__in=errorElements,datetime__range=(past,today)).order_by('-appversion','-osversion')

    appv_idx = -1
    for i in instances:
        print i.appversion, i.osversion
        if not i.appversion in categories:
            pre_osv = i.osversion
            appv_idx += 1
            categories.append(i.appversion)
        if not i.osversion in temp_data:
            temp_data[i.osversion] = []
        while len(temp_data[i.osversion]) <= appv_idx:
            temp_data[i.osversion].append(0)
        score = float(i.iderror.errorweight) / i.iderror.numofinstances
        print score
        temp_data[i.osversion][appv_idx] += score

    for t in temp_data:
        idx = 0
        for e in temp_data[t]:
            temp_data[t][idx] = round(e,2)
            idx += 1
        ver_data.append({'name':t,'data':temp_data[t]})

    print categories
    print ver_data

        #ver_data[appv_idx][]
    #print categories
    chart4 = {'categories':categories,'data':ver_data}
    result['chart4'] = chart4
    return HttpResponse(json.dumps(result), 'application/json');
