# Create your views here.

import time
import simplejson
from django.http import HttpResponse

def connect(request):
    sessionID = time.time()
    #return HttpResponse(sessionID)
    return HttpResponse(simplejson.dumps({'sessionID':sessionID}), 'application/json');

def receive_exception(request):

    return HttpResponse('test')

def receive_uncaught(request):

    return HttpResponse('test')

def receive_eventpath(request):

    return HttpResponse('test')