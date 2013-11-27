# Create your views here.
# -*- coding: utf-8 -*-

import time


from django.utils.timezone import utc
from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from urqa.models import Session

from soma3.settings import STATIC_URL

from oauth2client.client import OAuth2WebServerFlow

def index(request):
    print request.REQUEST
    print request.COOKIES

    flow = OAuth2WebServerFlow(client_id='659918816506-g8di1qo7d4n84imp7rh8vlsmp7e4511d.apps.googleusercontent.com',
                               client_secret='aHYr6xjCOmMO53cYHW64qQpr',
                               scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
                               redirect_uri='http://ur-qa.com/urqa/user/google_oauth2')
    #print flow
    auth_uri = flow.step1_get_authorize_url()
    print auth_uri
    #credentials = flow.step2_exchange('code')
    #print credentials

    if 'urqa_google_access_token' in request.COOKIES:
        print request.COOKIES['urqa_google_access_token']
    else:
        print 'no google access_token'



    redirect_uri = 'https://github.com/litl/rauth'

    #만약 로그인 되어 있다면!!
    if request.user.is_authenticated():
       return HttpResponseRedirect('/urqa/projects')

    ctx = {}
    #print request

    return render(request, 'login.html', ctx)

def google_oauth2(request):

    print request.REQUEST
    print ''
    print request
    return

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

def tutorialrequest(request, path):
    return HttpResponseRedirect(STATIC_URL + path)
