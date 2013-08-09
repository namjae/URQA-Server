# Create your views here.

import random
import simplejson
from django.http import HttpResponse

def connect(request):
    sessionID = random.randint(1,1000000)
    #return HttpResponse(sessionID)
    return HttpResponse(simplejson.dumps({'sessionID':sessionID}), 'application/json');
