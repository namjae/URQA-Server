# Create your views here.
# -*- coding: utf-8 -*-

import time
import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from client.models import Session
from client.models import Sessionevent

def connect(request):
    sessionID = long(time.time() * 1000000)
    #return HttpResponse(sessionID)
    return HttpResponse(simplejson.dumps({'sessionID':sessionID}), 'application/json');

@csrf_exempt
def receive_exception(request):

    return HttpResponse('test')

@csrf_exempt
def receive_uncaught(request):

    return HttpResponse('test')

@csrf_exempt
def receive_eventpath(request):

    jsonData = simplejson.loads(request.body)
    print jsonData
    sessionID = jsonData['sessionID']
    eventPath = jsonData['eventPath']

    print sessionID
    print eventPath

    for event in eventPath:
        print event.dateTime
        print event.className
        print event.methodName
        print event.lineNum
        s = Sessionevent(datetime=event.dateTime,classname=event.className,methodname=event.method,linenum=event.lineNum)
        print s
        #s.save()

    #eventPaths = request.POST['eventPaths'];
    #print Session.objects.exists(idsesstion=long(sessionID))
    entry = Session.objects.all()
    entry = entry.get(idsession=long(sessionID))
    print entry
    print entry.idsession
    print entry.appversion
    print entry.apikey
    return HttpResponse('test')