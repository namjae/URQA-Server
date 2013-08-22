# -*- coding: utf-8 -*-

import time
import datetime

from django.utils.timezone import utc

def getDatetime():
    now = time.localtime()
    return '%04d-%02d-%02d %02d:%02d:%02d' % (now.tm_year, now.tm_mon, now.tm_mday,
                                              now.tm_hour, now.tm_min, now.tm_sec)

def naive2aware(time_str):
    naivetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return naivetime.replace(tzinfo=utc)