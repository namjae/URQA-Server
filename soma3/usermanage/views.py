# Create your views here.
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

def logintest(request):
    tpl = loader.get_template('base.html')
    ctx = Context({})
    return HttpResponse(tpl.render(ctx))

def registration(request):
    print request

    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']


    if User.objects.filter(username__exact=username).exists():
        return HttpResponse('%s already exists' % username)

    user = User.objects.create_user(username,email,password)
    user.save()
    return HttpResponse('success registration')

def delete_req(request):
    try:
        user = User.objects.get(username__exact=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('%s not exists' % request.user)

    user.delete()

    return HttpResponse('delete success')

def login_req(request):
    print request.user
    print request
    username = request.POST['username']
    password = request.POST['password']

    print username
    print password

    user = authenticate(username=username, password=password)
    print user
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse('success')
        else:
            return HttpResponse('disable account')
    else:
        return HttpResponse('invalid login')
    return HttpResponse('login')

def logout_req(request):
    print request.user
    logout(request)
    return HttpResponse('logout success')