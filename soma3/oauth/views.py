# Create your views here.
# -*- coding: utf-8 -*-

import os
import json
import httplib2
from soma3 import settings

from urqa.models import AuthUser
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from oauth2client.client import flow_from_clientsecrets
from oauth2client import xsrfutil
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

from config import get_config


CLIENT_SECRETS = get_config('GOOGLE_OAUTH_PATH')
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
                                   scope="https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
                                   redirect_uri="http://urqa.io/urqa/user/auth_return")

def login_by_google(request):
    #Google login을 사용하기위한 API적용
    print 'login_by_google', request.user
    SK = request.POST['csrfmiddlewaretoken']
    #FLOW.params['state'] = xsrfutil.generate_token(SECRET_KEY,request.user)
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)




def auth_return(request):
    #Google Oauth기능 구현

    print request.REQUEST
    if 'error' in request.REQUEST:
        return HttpResponseRedirect('/')
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user):
        return  HttpResponseBadRequest()

    credential = FLOW.step2_exchange(request.REQUEST)

    http = httplib2.Http()
    http = credential.authorize(http)

    #Google은 oauth2라이브러리를 사용하여 받을 수 잇음
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()



    #Google로부터 User Email, Unique ID를 얻어온다.
    username = 'google:' + user_document['email']
    password = user_document['id']

    #Google Oauth를 처음 사용하는 유저라면 ID를 생성한다.
    user = authenticate(username=username, password=password)
    print user
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/urqa/projects')
    # 처음생성된 ID라면 ID등록함


    email = user_document['email']
    first_name = user_document['name']
    image_path = user_document['picture']


    if User.objects.filter(username__exact=username).exists():
        return HttpResponseRedirect('/urqa/')
        #return HttpResponse('%s already exists' % username)

    user = User.objects.create_user(username,email,password)
    user.first_name = first_name
    user.save()

    user = AuthUser.objects.get(username = username)
    user.image_path = image_path

    user.save()
    user = authenticate(username=username, password=password)
    login(request, user)
    return HttpResponseRedirect('/urqa/projects')
