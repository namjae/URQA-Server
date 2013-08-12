# Create your views here.
# -*- coding: utf-8 -*-

import time
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from client.models import Session
from client.models import Sessionevent
from client.models import Errors
from client.models import Projects

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

    #apikey가 validate한지 확인하기.
    try:
        apikey = jsonData['apikey']
        proejctElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print "Invalid apikey"
        return HttpResponse('Invalid apikey')

    errorname = jsonData['errorname']
    errorclassname = jsonData['errorclassname']
    linenum = jsonData['linenum']

    print errorname
    print errorclassname
    print linenum

    if Errors.objects.filter(errorname=errorname,errorclassname=errorclassname,linenum=linenum).exists():
        print "here!"
        print "here!"
        print "here!"
        print "here!"

    return HttpResponse('test')

@csrf_exempt
def receive_exception_log(request):

    return HttpResponse('test');

@csrf_exempt
def receive_eventpath(request):

    jsonData = json.loads(request.body,encoding='utf-8')
    print jsonData
    idsession = long(jsonData['idsession'])
    eventpath = jsonData['eventpaths']

    session_key = Session.objects.get(idsession=idsession)
    for event in eventpath:
        Sessionevent.objects.create(idsession=session_key,
                                    datetime=event['datetime'],
                                    classname=event['classname'],
                                    methodname=event['methodname'],
                                    linenum=int(event['linenum']))

    return HttpResponse('done')