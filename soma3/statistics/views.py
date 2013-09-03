# Create your views here.
# -*- coding: utf-8 -*-

from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from common import validUserPjt

from utility import getTimeRange
from utility import TimeRange
from utility import Status

from urqa.models import AuthUser
from urqa.models import Errors
from urqa.models import Projects


def statistics(request,pid):
    username = request.user

    valid , message , userelement, projectelement = validUserPjt(username,pid)

    if not valid:
        return HttpResponseRedirect('/urqa')

    user = AuthUser.objects.get(username = request.user)

    tpl = loader.get_template('statistics.html')
    ctx = Context({
        'ServerURL' : 'http://'+request.get_host() + '/urqa/project/',
        'projectid' : pid,
        'user_name' :user.first_name + ' ' + user.last_name ,
        'user_email': user.email,
        'profile_url' : user.image_path,
    });
    return HttpResponse(tpl.render(ctx))

def byclass(request,pid):
    username = request.user
    valid , message , userElement, projectElement = validUserPjt(username,pid)
    if not valid:
        return HttpResponseRedirect('/urqa')

    week, today = getTimeRange(TimeRange.monthly)

    errorElement = Errors.objects.filter(pid=projectElement,status__in=[Status.New,Status.Open,Status.Renew],lastdate__range=(week,today)).order_by('errorclassname','errorweight')

    for e in errorElement:
        print e.iderror, e.status, e.errorclassname, e.errorweight

    return HttpResponse('hello')

def bydevice(request,pid):
    return True

def byactivity(request,pid):
    return True

def byversion(request,pid):
    return True