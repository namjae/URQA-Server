# Create your views here.
# -*- coding: utf-8 -*-

import time
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from client.models import Session
from client.models import Sessionevent


@csrf_exempt
def connect(request):
    idsession = long(time.time() * 1000000)
    jsonData = json.loads(request.body,encoding='utf-8')
    session = Session(idsession=idsession,apikey=jsonData['apikey'],appversion=jsonData['appversion'])

    return HttpResponse(simplejson.dumps({'idsession':idsession}), 'application/json');

@csrf_exempt
def receive_exception(request):

    return HttpResponse('test')

@csrf_exempt
def receive_uncaught(request):

    return HttpResponse('test')

@csrf_exempt
def receive_eventpath(request):

    jsonData = json.loads(request.body,encoding='utf-8')
    print jsonData
    sessionID = long(jsonData['idsession'])
    eventPath = jsonData['eventPath']

    print sessionID
    print len(eventPath)
    print eventPath[0]
    i = 0
    entry = Session.objects.all()
    entry = entry.get(idsession=long(sessionID))
    for event in eventPath:
        s = Sessionevent(idsession=entry,datetime=event['dateTime'],classname=event['className'],methodname=event['methodName'],linenum=int(event['lineNum']))
        print s
        s.save()

    #eventPaths = request.POST['eventPaths'];
    #print Session.objects.exists(idsesstion=long(sessionID))
    entry = Session.objects.all()
    entry = entry.get(idsession=long(sessionID))
    print entry
    print entry.idsession
    print entry.appversion
    print entry.apikey
    return HttpResponse('test')