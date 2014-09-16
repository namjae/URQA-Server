# Create your views here.
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from soma3.settings import STATIC_URL
# from utility import getUTCawaredatetime

# from oauth2client.client import OAuth2WebServerFlow
from soma3.settings import PROJECT_DIR
def index(request):
    return render(request, 'index.html')

def login(request):

    #만약 로그인 되어 있다면!!
    if request.user.is_authenticated():
       return HttpResponseRedirect('/urqa/projects')

    ctx = {}
    #print request
    return render(request, 'login.html', ctx)

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
    #expire_time = long(0.5 * 24 * 60 * 60 * 1000) # 1일
    #expire_time = long(time.time() * 1000) - expire_time

    #elements = Session.objects.filter(idsession__lt=expire_time)

    #elements.delete()
    """
    appruncountElement = Appruncount.objects.filter(date__lt='2014-07-25')
    appruncount2Element = Appruncount2.objects.filter(datetime__lt='2014-07-25 00:00:00+00:00')

    print >> sys.stderr,len(appruncount2Element);
    appruncount2Element.delete()
    i = 1

    for e in appruncountElement:
        if e.date == None or e.appversion == None or e.runcount == None:
            print  >> sys.stderr,'error',e.pid,e.date,e.appversion,e.runcount
            continue
        Appruncount2.objects.create(pid=e.pid,appversion=e.appversion,appruncount=e.runcount,datetime='%s 00:00:00+00:00' % e.date)
        print >> sys.stderr, i, e.date
        i = i + 1
    """
    return HttpResponse('clean up')


def mediapathrequest(request, path):
    return HttpResponseRedirect(STATIC_URL+path)

def tutorialrequest(request, path):
    return HttpResponseRedirect(STATIC_URL + path)

def unity_crossdomain(request):
    abspath = open(PROJECT_DIR + '/templates/crossdomain.xml','r')
    response = HttpResponse(content=abspath.read())
    response['Content-Type']= 'application/xml'
    response['Content-Disposition'] = 'attachment; filename=crossdomain.xml';
    return response
    #ctx = {}
    #print request
    #return render(request, 'crossdomain.xml', ctx)
