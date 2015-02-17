# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Activitystatistics(models.Model):
    idactivitystatistics = models.AutoField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    activityname = models.CharField(max_length=300)
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'activitystatistics'

class Appruncount(models.Model):
    idappruncount = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    date = models.DateField(blank=True, null=True)
    appversion = models.CharField(max_length=45, blank=True)
    runcount = models.BigIntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'appruncount'

class Appruncount2(models.Model):
    idappruncount = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    datetime = models.DateTimeField(blank=True, null=True)
    appversion = models.CharField(max_length=45, blank=True)
    appruncount = models.BigIntegerField(blank=True, null=True)
    class Meta:
        managed = False
        unique_together = ('pid', 'datetime', 'appversion')
        db_table = 'appruncount2'

class Appstatistics(models.Model):
    idappstatistics = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    iderror = models.ForeignKey('Errors', db_column='iderror')
    appversion = models.CharField(max_length=45)
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'appstatistics'

class AuthGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    image_path = models.CharField(max_length=260, blank=True)
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'

class Comments(models.Model):
    idcomment = models.AutoField(primary_key=True)
    uid = models.ForeignKey(AuthUser, db_column='uid')
    iderror = models.ForeignKey('Errors', db_column='iderror')
    datetime = models.DateTimeField()
    comment = models.CharField(max_length=200)
    class Meta:
        managed = False
        db_table = 'comments'

class Countrystatistics(models.Model):
    idcountrystatistics = models.AutoField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    countryname = models.CharField(max_length=45)
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'countrystatistics'

class Devicestatistics(models.Model):
    iddevicestatistics = models.AutoField(primary_key=True)
    iderror = models.ForeignKey('Errors', db_column='iderror')
    devicename = models.CharField(max_length=45)
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'devicestatistics'

class DjangoContentType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'

class DjangoSite(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'django_site'

class Errors(models.Model):
    iderror = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    rank = models.IntegerField()
    autodetermine = models.IntegerField()
    status = models.IntegerField(blank=True, null=True)
    numofinstances = models.IntegerField()
    createdate = models.DateTimeField()
    lastdate = models.DateTimeField()
    callstack = models.TextField()
    errorname = models.CharField(max_length=500)
    errorclassname = models.CharField(max_length=300)
    linenum = models.CharField(max_length=45)
    errorweight = models.IntegerField(blank=True, null=True)
    recur = models.IntegerField(blank=True, null=True)
    eventpath = models.TextField(blank=True)
    wifion = models.IntegerField()
    gpson = models.IntegerField()
    mobileon = models.IntegerField()
    totalmemusage = models.IntegerField()
    gain1 = models.FloatField(blank=True, null=True)
    gain2 = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'errors'

class Eventpaths(models.Model):
    ideventpaths = models.AutoField(primary_key=True)
    idinstance = models.ForeignKey('Instances', db_column='idinstance')
    iderror = models.ForeignKey(Errors, db_column='iderror')
    ins_count = models.IntegerField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    classname = models.CharField(max_length=300, blank=True)
    methodname = models.CharField(max_length=300, blank=True)
    linenum = models.IntegerField(blank=True, null=True)
    depth = models.IntegerField(blank=True, null=True)
    label = models.CharField(max_length=300, blank=True)
    class Meta:
        managed = False
        db_table = 'eventpaths'

class Instances(models.Model):
    idinstance = models.AutoField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    ins_count = models.IntegerField(blank=True, null=True)
    sdkversion = models.CharField(max_length=45, blank=True)
    appversion = models.CharField(max_length=45, blank=True)
    osversion = models.CharField(max_length=45, blank=True)
    kernelversion = models.CharField(max_length=45, blank=True)
    appmemmax = models.CharField(max_length=45, blank=True)
    appmemfree = models.CharField(max_length=45, blank=True)
    appmemtotal = models.CharField(max_length=45, blank=True)
    country = models.CharField(max_length=45, blank=True)
    datetime = models.DateTimeField(blank=True, null=True)
    locale = models.CharField(max_length=45, blank=True)
    mobileon = models.IntegerField(blank=True, null=True)
    gpson = models.IntegerField(blank=True, null=True)
    wifion = models.IntegerField(blank=True, null=True)
    device = models.CharField(max_length=45, blank=True)
    rooted = models.IntegerField(blank=True, null=True)
    scrheight = models.IntegerField(blank=True, null=True)
    scrwidth = models.IntegerField(blank=True, null=True)
    scrorientation = models.IntegerField(blank=True, null=True)
    sysmemlow = models.CharField(max_length=45, blank=True)
    log_path = models.CharField(max_length=260, blank=True)
    batterylevel = models.IntegerField(blank=True, null=True)
    availsdcard = models.IntegerField(blank=True, null=True)
    xdpi = models.FloatField(blank=True, null=True)
    ydpi = models.FloatField(blank=True, null=True)
    callstack = models.TextField(blank=True)
    dump_path = models.CharField(max_length=260, blank=True)
    lastactivity = models.CharField(max_length=300, blank=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    class Meta:
        managed = False
        unique_together= (('pid', 'datetime'), ('iderror', 'appversion'),
                        ('iderror', 'osversion'), ('iderror', 'device'),
                        ('iderror', 'country'), ('iderror', 'wifion'),
                        ('iderror', 'gpson'),('iderror', 'mobileon'),
                        ('pid', 'datetime', 'country'))

        db_table = 'instances'

class Osstatistics(models.Model):
    idosstatistics = models.AutoField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    osversion = models.CharField(max_length=10)
    pid = models.ForeignKey('Projects', db_column="pid")
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'osstatistics'

class Proguardmap(models.Model):
    idproguardmap = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Projects', db_column='pid')
    appversion = models.CharField(max_length=45, blank=True)
    filename = models.CharField(max_length=45, blank=True)
    uploadtime = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'proguardmap'

class Projects(models.Model):
    pid = models.AutoField(primary_key=True)
    apikey = models.CharField(unique=True, max_length=10)
    platform = models.IntegerField()
    name = models.CharField(max_length=45)
    stage = models.IntegerField()
    owner_uid = models.ForeignKey(AuthUser, db_column='owner_uid')
    category = models.IntegerField(blank=True, null=True)
    timezone = models.CharField(max_length=45, blank=True)
    class Meta:
        managed = False
        db_table = 'projects'

class Session(models.Model):
    idsession = models.BigIntegerField(primary_key=True)
    pid = models.ForeignKey(Projects, db_column='pid')
    appversion = models.CharField(max_length=45)
    class Meta:
        managed = False
        db_table = 'session'

class Sessionevent(models.Model):
    idsessionevent = models.AutoField(primary_key=True)
    idsession = models.ForeignKey(Session, db_column='idsession')
    datetime = models.DateTimeField(blank=True, null=True)
    classname = models.CharField(max_length=300, blank=True)
    methodname = models.CharField(max_length=300, blank=True)
    linenum = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'sessionevent'

class Sofiles(models.Model):
    idsofiles = models.AutoField(primary_key=True)
    pid = models.ForeignKey(Projects, db_column='pid')
    appversion = models.CharField(max_length=45)
    versionkey = models.CharField(max_length=45, blank=True)
    filename = models.CharField(max_length=45, blank=True)
    uploaded = models.CharField(max_length=45, blank=True)
    class Meta:
        managed = False
        db_table = 'sofiles'

class Tags(models.Model):
    idtag = models.AutoField(primary_key=True)
    iderror = models.ForeignKey(Errors, db_column='iderror')
    tag = models.CharField(max_length=45)
    pid = models.ForeignKey(Projects, db_column='pid', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'tags'

class Users(models.Model):
    uid = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=45)
    passwd = models.CharField(max_length=20)
    nickname = models.CharField(max_length=45)
    company = models.CharField(max_length=45)
    image_path = models.CharField(max_length=45, blank=True)
    class Meta:
        managed = False
        db_table = 'users'

class Viewer(models.Model):
    idviewer = models.AutoField(primary_key=True)
    uid = models.ForeignKey(AuthUser, db_column='uid')
    pid = models.ForeignKey(Projects, db_column='pid')
    class Meta:
        managed = False
        db_table = 'viewer'

class ProjectSummary(models.Model):
    instanceCount = models.IntegerField()
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    apikey = models.CharField(max_length=10)
    owner_uid = models.CharField(max_length=10)
    platform = models.IntegerField()
    stage = models.IntegerField()
    #runcount = models.IntegerField()
    class Meta:
         managed = False
         db_table = 'projectsummary'

class ErrorsbyApp(models.Model):
    errorcount = models.IntegerField(primary_key=True)
    appversion = models.CharField(max_length=45, blank=True)
    errorday = models.CharField(max_length=45, blank=True)

class SessionbyApp(models.Model):
    idsessionbyapp = models.IntegerField(primary_key=True)
    runcount = models.IntegerField(blank=True, null=True)
    appversion = models.CharField(max_length=45, blank=True)
    sessionday = models.CharField(max_length=45, blank=True)

class ErrorbyRank(models.Model):
    iderrorbyrank = models.IntegerField(primary_key=True)
    errorcount = models.IntegerField(blank=True, null=True)
    errorrank = models.IntegerField(blank=True, null=True)

class CountrysbyApp(models.Model):
   count = models.IntegerField(primary_key=True)
   country = models.CharField(max_length=45, blank=True)

class InstanceCountModel(models.Model):
    iderror = models.IntegerField(primary_key=True)
    count = models.IntegerField(blank=True, null=True)

class ErrorStatistics(models.Model):
    iderrorstatistics = models.IntegerField(primary_key=True)
    keyname = models.CharField(max_length=45, blank=True)
    count = models.IntegerField(blank=True, null=True)

class Erbd(models.Model):
    device = models.CharField(max_length=45, primary_key=True)
    sum = models.IntegerField(blank=True, null=True)

class Erba(models.Model):
    activity = models.CharField(max_length=255, primary_key=True)
    sum = models.IntegerField(blank=True, null=True)

class Erbv(models.Model):
    appversion = models.CharField(max_length=255, primary_key=True)
    osversion = models.CharField(max_length=255)
    sum = models.IntegerField(blank=True, null=True)

class ErbvApps(models.Model):
    appversion = models.CharField(max_length=255, primary_key=True)
    sum = models.IntegerField(blank=True, null=True)

class TotalSession(models.Model):
    appversion = models.CharField(max_length=255, primary_key=True)
    total = models.IntegerField(blank=True, null=True)

class LoginErrorCountModel(models.Model):
    pid = models.IntegerField(primary_key=True)
    count = models.IntegerField(blank=True, null=True)

class LoginApprunCount(models.Model):
    pid = models.IntegerField(primary_key=True)
    count = models.IntegerField(blank=True, null=True)

class InstanceLog(models.Model):
    idinstance = models.IntegerField(primary_key=True)
    log = models.TextField(blank=True, null=True)
    savetime = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'instancelog'


