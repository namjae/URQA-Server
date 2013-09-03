# Create your views here.
# -*- coding: utf-8 -*-

import json

from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from common import validUserPjt

from utility import getTimeRange
from utility import TimeRange
from utility import Status

from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Devicestatistics
from urqa.models import Instances
from urqa.models import Projects


def statistics(request,pid):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('statistics.html')
    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email,
        'profile_url' : user.image_path,
    });
    return HttpResponse(tpl.render(ctx))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def chartdata(request,pid):
    jsonData = json.loads(request.POST['json'],encoding='utf-8')
    retention = jsonData['retention']

    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,pid)
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
    instances = Instances.objects.filter(iderror__in=errorElements,datetime__range=(past,today)).order_by('-appversion','-osversion')
    for i in instances:
        if not i.appversion in categories:
            categories.append(i.appversion)
            ver_data.append({'name':i.appversion,'data':[]})

    print categories
    chart4 = {'categories':categories,'data':ver_data}
    return HttpResponse(json.dumps(result), 'application/json');
