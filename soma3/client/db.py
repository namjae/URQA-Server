# Create your views here.

import time
import simplejson
from django.http import HttpResponse
from client.models import Instances
from django.views.decorators.csrf import csrf_exempt
"""
def connect(request):
    sessionID = time.time()
    #return HttpResponse(sessionID)
    return HttpResponse(simplejson.dumps({'sessionID':sessionID}), 'application/json');

def receive_exception(request):

    return HttpResponse('test')

def receive_uncaught(request):

    return HttpResponse('test')

def receive_eventpath(request):
    sessionID = request.POST['sessionID'];
    eventPaths = request.POST['eventPaths'];
    Session.objects.get(idsesstion=long(sessionID))
    return HttpResponse('test')
"""
@csrf_exempt
def receive_ErrorData(request):
	instances = Instances.objects.all();
	#instances = Instances(iderror = 1 ,rank = request.POST['rank'], 
	#str = print(instances);
	return HttpResponse(instances)