# -*- coding: utf-8 -*-

import time
import datetime
import os

from django.utils.timezone import utc

def getDatetime():
    now = time.localtime()
    return '%04d-%02d-%02d %02d:%02d:%02d' % (now.tm_year, now.tm_mon, now.tm_mday,
                                              now.tm_hour, now.tm_min, now.tm_sec)

def naive2aware(time_str):
    naivetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return naivetime.replace(tzinfo=utc)


def getProjectPath():
    project_path = os.path.realpath(os.path.dirname(__file__))
    return project_path

def getTemplatePath():
    return getProjectPath() + '/templates/'

class RANK:
    toString = ['Unhandle','Critical','Major','Minor','Native']
    Suspense = -1
    Unhandle = 0
    Critical = 1
    Major    = 2
    Minor    = 3
    Native   = 4

class TimeRange:
    oneday = 1
    weekly = 7
    monthly = 30
    threemonthly = 90

class Status:
    toString = ['New','Open','Ignore','Renew']
    New = 0
    Open = 1
    Ignore = 2
    Renew = 3
#weekly, monthly, 3monthly
def getTimeRange(t):

    today = datetime.datetime.utcnow().replace(tzinfo=utc)
    #today = today.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

    datedelta = datetime.timedelta(days =  -(t - 1))

    past = today + datedelta
    past = past.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

    return past, today
