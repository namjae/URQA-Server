# Create your views here.
# -*- coding: utf-8 -*-

import json
import operator

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
from urqa.models import Activitystatistics
from urqa.models import Instances


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
    errorElements = Errors.objects.filter(pid=projectElement,status__in=[Status.New,Status.Open],lastdate__range=(past,today)).order_by('errorclassname','errorweight')
    instanceElements = Instances.objects.select_related().filter(iderror__in=errorElements,datetime__range=(past,today))
    #Chart1
    chart1 = []
    pre_class = ''
    print 'past',past
    for e in errorElements:
        instanceCount = Instances.objects.filter(iderror=e,datetime__gte=past).count()
        if pre_class != e.errorclassname:
            pre_class = e.errorclassname
            chart1.append([e.errorclassname, instanceCount])
        else:
            last = len(chart1)
            chart1[last-1] = [e.errorclassname,chart1[last-1][1] + (instanceCount)]


    result = {}
    result['chart1'] = chart1

    #Chart2
    chart2 = []
    temp_data = {}
    activities = []
    instances = instanceElements.order_by('device')
    for i in instances:
        if i.device:
            device = i.device
        else:
            device = "Unknown"
        if not device in activities:
            activities.append(device)
            temp_data[device] = 1
        else:
            temp_data[device] += 1
    sorted_dic = sorted(temp_data.iteritems(), key=operator.itemgetter(1), reverse=True)
    for l,v in sorted_dic:
        chart2.append({
            'label': l,
            'value': v,
        })
    result['chart2'] = chart2
    """chart2 = []
    temp_data = {}
    for e in errorElements:
        devices = Devicestatistics.objects.filter(iderror=e).order_by('devicename')
        if devices.count() == 0:
            continue
        total = 0
        for d in devices:
            total += d.count

        for d in devices:
            if not d.devicename in temp_data:
                temp_data[d.devicename] = e.errorweight * d.count / total
            else:
                temp_data[d.devicename] += e.errorweight * d.count / total
    sorted_dic = sorted(temp_data.iteritems(), key=operator.itemgetter(1), reverse=True)
    for l,v in sorted_dic:
        chart2.append({
            'label': l,
            'value': v,
        })

    result['chart2'] = chart2"""

    #Chart3
    chart3 = []
    temp_data = {}
    activities = []
    instances = instanceElements.order_by('lastactivity')
    for i in instances:
        if i.lastactivity:
            lastactivity = i.lastactivity
        else:
            lastactivity = "Unknown"
        if not lastactivity in activities:
            activities.append(lastactivity)
            temp_data[lastactivity] = 1
        else:
            temp_data[lastactivity] += 1
    sorted_dic = sorted(temp_data.iteritems(), key=operator.itemgetter(1), reverse=True)
    for l,v in sorted_dic:
        chart3.append({
            'label': l,
            'value': v,
        })
    result['chart3'] = chart3
    """temp_data = {}
    for e in errorElements:
        activity = Activitystatistics.objects.filter(iderror=e).order_by('activityname')
        if devices.count() == 0:
            continue
        total = 0
        for d in activity:
            print d.activityname
            total += d.count
            #print d.devicename
        #print total,e.errorweight

        for d in activity:
            if not d.activityname in temp_data:
                temp_data[d.activityname] = e.errorweight * d.count / total
            else:
                temp_data[d.activityname] += e.errorweight * d.count / total

    sorted_dic = sorted(temp_data.iteritems(), key=operator.itemgetter(1), reverse=True)
    for l,v in sorted_dic:
        chart3.append({
            'label': l,
            'value': v,
        })
    """


    #Chart4
    categories = []
    ver_data = []
    temp_data = {}
    instances = instanceElements.order_by('-appversion','-osversion')

    appv_idx = -1
    for i in instances:
        if not i.appversion in categories:
            appv_idx += 1
            categories.append(i.appversion)
        if not i.osversion in temp_data:
            temp_data[i.osversion] = []
        while len(temp_data[i.osversion]) <= appv_idx:
            temp_data[i.osversion].append(0)
        #score = float(i.iderror.errorweight) / i.iderror.numofinstances
        temp_data[i.osversion][appv_idx] += 1#score

    for t in temp_data:
        idx = 0
        for e in temp_data[t]:
            temp_data[t][idx] = e#round(e,2)
            idx += 1
        ver_data.append({'name':t,'data':temp_data[t]})

    #print categories
    #print ver_data

        #ver_data[appv_idx][]
    #print categories
    chart4 = {'categories':categories,'data':ver_data}
    result['chart4'] = chart4
    return HttpResponse(json.dumps(result), 'application/json');
