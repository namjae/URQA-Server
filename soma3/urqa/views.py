# Create your views here.
# -*- coding: utf-8 -*-

import time
import datetime
from django.utils.timezone import utc
from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from urqa.models import Session

from soma3.settings import STATIC_URL

def index(request):
#	return HttpResponse('hello world')
    tpl = loader.get_template('test.html')
    ctx = Context({});
    #return HttpResponse(tpl.render(ctx))

    #now = datetime.datetime.now()
    #now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)

    #print now
    #print now_utc
    #print timezone.now()
    #print timezone.make_naive(timezone.now(),datetime.tzinfo)
    return HttpResponse(str(request.user) + ' ' + str(request.user.is_authenticated()))


@csrf_exempt
def adduser(request):
    print request
    #print request.POST['email']
    #print request.POST['passwd']
    #print request.POST['nick']
    #print request.POST['company']

    str = request.POST['email']# + request.POST['passwd'] + request.POST['nick'] + request.POST['company']
    #request.
    return HttpResponse('hello world ' + str);


def posttest(request):
    print request.user
    c = {}
    return render(request, 'posttestmodule.html', c)

def fileuploadtest(request):
    c = {}
    return render(request, 'fileupload.html', c)

def cleanup(request):
    expire_time = long(0.5 * 24 * 60 * 60 * 1000) # 1일
    expire_time = long(time.time() * 1000) - expire_time

    elements = Session.objects.filter(idsession__lt=expire_time)

    elements.delete()

    return HttpResponse('clean up')


def mediapathrequest(request, path):
    return HttpResponseRedirect(STATIC_URL+path)

