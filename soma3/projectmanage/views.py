# Create your views here.
# -*- coding: utf-8 -*-

import random

from django.http import HttpResponse
from django.contrib.auth.models import User
from client.models import AuthUser
from django.core.exceptions import ObjectDoesNotExist
from client.models import Projects

def newApikey():
    while True:
        apikey = "%08d" % random.randint(1,99999999)
        if not Projects.objects.filter(apikey=apikey).exists():
            break
    return apikey


def registration(request):
    print request.user

    try:
        owner = AuthUser.objects.get(username=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('user "%s" not exists' % request.user)

    print owner
    name = request.POST['name']
    platform = int(request.POST['platform'])
    stage = int(request.POST['stage'])


    if Projects.objects.filter(owner_uid=owner,name=name).exists():
        return HttpResponse('project %s already exists' % name)

    apikey = newApikey()
    print 'new apikey = %s' % apikey

    projectElement = Projects.objects.create(owner_uid=owner,apikey=apikey,name=name,platform=platform,stage=stage)
    return HttpResponse('success registration')

def delete_req(request):
    try:
        user = User.objects.get(username__exact=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('%s not exists' % request.user)

    user.delete()

    return HttpResponse('delete success')