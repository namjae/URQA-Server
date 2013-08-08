# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Appstatistics(models.Model):
    appstatisticsid = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    appversion = models.CharField(max_length=10L)
    count = models.IntegerField()
    class Meta:
        db_table = 'appstatistics'

class Comments(models.Model):
    commentsid = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    date = models.DateTimeField()
    user = models.ForeignKey('Users', db_column='user')
    comment = models.CharField(max_length=45L)
    class Meta:
        db_table = 'comments'

class Countrystatistics(models.Model):
    countrystatisticsid = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    countryname = models.CharField(max_length=45L)
    count = models.IntegerField()
    class Meta:
        db_table = 'countrystatistics'

class Devicestatistics(models.Model):
    devicestatisticsid = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    devicename = models.CharField(max_length=45L)
    count = models.IntegerField()
    class Meta:
        db_table = 'devicestatistics'

class Errors(models.Model):
    iderror = models.IntegerField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    rank = models.IntegerField()
    status = models.IntegerField(null=True, blank=True)
    numofinstances = models.IntegerField()
    createdate = models.DateTimeField()
    lastdate = models.DateTimeField()
    callstack = models.CharField(max_length=45L)
    classname = models.CharField(max_length=45L)
    filename = models.CharField(max_length=45L)
    line = models.CharField(max_length=45L)
    autodetermine = models.IntegerField()
    errorweight = models.IntegerField(null=True, blank=True)
    recur = models.IntegerField(null=True, blank=True)
    eventpath = models.TextField(blank=True)
    wifion = models.IntegerField()
    gpson = models.IntegerField()
    mobileon = models.IntegerField()
    totalmemusage = models.IntegerField()
    class Meta:
        db_table = 'errors'

class Eventpaths(models.Model):
    idinstance = models.ForeignKey('Instances', db_column='idinstance')
    event = models.CharField(max_length=45L, blank=True)
    eventpathsid = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'eventpaths'

class Instances(models.Model):
    idinstance = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    sdkversion = models.CharField(max_length=45L, blank=True)
    appversion = models.CharField(max_length=45L, blank=True)
    osversion = models.CharField(max_length=45L, blank=True)
    appmemmax = models.CharField(max_length=45L, blank=True)
    appmemavail = models.CharField(max_length=45L, blank=True)
    appmemtotal = models.CharField(max_length=45L, blank=True)
    country = models.CharField(max_length=45L, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    locale = models.CharField(max_length=45L, blank=True)
    mobileon = models.CharField(max_length=45L, blank=True)
    gpson = models.CharField(max_length=45L, blank=True)
    wifion = models.CharField(max_length=45L, blank=True)
    device = models.CharField(max_length=45L, blank=True)
    rooted = models.CharField(max_length=45L, blank=True)
    scrheight = models.CharField(max_length=45L, blank=True)
    scrwidth = models.CharField(max_length=45L, blank=True)
    srcorientation = models.CharField(max_length=45L, blank=True)
    sysmemlow = models.CharField(max_length=45L, blank=True)
    eventpath = models.CharField(max_length=45L, blank=True)
    log_path = models.CharField(max_length=45L, blank=True)
    class Meta:
        db_table = 'instances'

class Osstatistics(models.Model):
    osstatisticsid = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    osversion = models.CharField(max_length=10L)
    count = models.IntegerField()
    class Meta:
        db_table = 'osstatistics'

class Projects(models.Model):
    pid = models.IntegerField(unique=True)
    apikey = models.CharField(max_length=10L, unique=True)
    platform = models.IntegerField()
    name = models.CharField(max_length=45L)
    stage = models.IntegerField()
    class Meta:
        db_table = 'projects'

class Tags(models.Model):
    idtag = models.IntegerField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    tag = models.CharField(max_length=45L)
    class Meta:
        db_table = 'tags'

class Users(models.Model):
    uid = models.IntegerField(unique=True)
    email = models.CharField(max_length=45L, unique=True)
    passwd = models.CharField(max_length=20L)
    nickname = models.CharField(max_length=45L)
    company = models.CharField(max_length=45L)
    image_path = models.CharField(max_length=45L, blank=True)
    class Meta:
        db_table = 'users'

class Viewer(models.Model):
    uid = models.ForeignKey(Users, db_column='uid')
    pid = models.ForeignKey(Projects, db_column='pid')
    class Meta:
        db_table = 'viewer'
