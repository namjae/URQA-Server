# -*- coding: utf-8 -*-

import json
import pytz

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import utc

from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Errors
from urqa.models import Viewer

from utility import get_dict_value_matchin_key
from utility import get_dict_value_matchin_number

from config import get_config


def validUserPjtError(username, pid, iderror):

    result, msg, userElement, projectElement = validUserPjt(username,pid)
    if result == False:
        return result, msg, userElement, projectElement, None

    # Project에 Error ID 가 정상적으로 포함되어있는지 확인
    try:
        errorElement = Errors.objects.get(iderror=iderror,pid=projectElement)
    except ObjectDoesNotExist:
        return False, 'Project "%s" have no error id %s' % (pid, iderror), userElement, projectElement, None

    return True, 'success', userElement, projectElement, errorElement


def validUserPjt(username,apikey):
    # User가 로그인되어있는지 확인
    try:
        userElement = AuthUser.objects.get(username=username)
    except ObjectDoesNotExist:
        #login url로 이동하
        return False, 'user "%s" not exists' % username, None, None

    # Project가 정상적으로 존재하는지 확인
    try:
        projectElement = Projects.objects.get(apikey=apikey)
    except ObjectDoesNotExist:
        print 'Fatal error'
        return False, 'Invalid project id %s' % apikey, userElement, None

    # User가 Project에 권한이 있는지 확인
    try:
        viewerElement = Viewer.objects.get(uid=userElement, pid=projectElement)
    except ObjectDoesNotExist:
        return False, 'user "%s" have no permission %s' % (username, apikey), userElement, projectElement

    return True, 'success', userElement, projectElement

def getUserProfileDict(userelement):
    dict = {'user_name' : userelement.first_name + ' ' + userelement.last_name , 'user_email' : userelement.email, 'profile_url':  userelement.image_path}
    return dict

def getApikeyDict(apikey):
    dict = {'projectid' : apikey }
    return dict

def getSettingDict(projectelement,userelement):

    isowner = False
    if(projectelement.owner_uid.id == userelement.id):
        isowner = True

    categorydata = json.loads(get_config('app_categories'))
    platformdata = json.loads(get_config('app_platforms'))
    stagedata = json.loads(get_config('app_stages'))

    platformnum = get_dict_value_matchin_number(platformdata,projectelement.platform)
    categorynum = get_dict_value_matchin_number(categorydata,projectelement.category)
    stagenum = get_dict_value_matchin_number(stagedata,projectelement.stage)

    platformtxt = get_dict_value_matchin_key(platformdata,projectelement.platform)

    count = 0
    for zone in pytz.common_timezones:
        if( zone == projectelement.timezone):
            break;
        count += 1

    viewerlist = []



    ViewerElements = Viewer.objects.select_related().filter(~Q(uid= userelement.id) ,pid = projectelement.pid)
    for v in ViewerElements:
        a = v.uid
        viewerlist.append(a.username)

    dict = {
        'platform_number' : platformnum + 1,
        'stage_number' : stagenum + 1,
        'category_number' : categorynum + 1,
        'timezonelist' : pytz.common_timezones,
        'timezone_number' : count + 1,
        'project_viewerlist' : viewerlist,
        'owner_user' : isowner,
        'app_platformlist' : platformdata.items(),
        'app_categorylist' : categorydata.items(),
        'app_stagelist' : stagedata.items(),
        'project_name' : projectelement.name,
        'project_platform' : platformtxt,
    }
    return dict


