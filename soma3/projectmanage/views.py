# Create your views here.
# -*- coding: utf-8 -*-

import os
import random
import subprocess

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


from common import validUserPjt
from urqa.models import AuthUser
from urqa.models import Projects
from urqa.models import Viewer

def newApikey():
    while True:
        apikey = "%08d" % random.randint(1,99999999)
        if not Projects.objects.filter(apikey=apikey).exists():
            break
    return apikey


def registration(request):
    #step1: login user element가져오기
    try:
        userElement = AuthUser.objects.get(username=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('user "%s" not exists' % request.user)

    name = request.POST['name']
    platform = int(request.POST['platform'])
    stage = int(request.POST['stage'])

    #project name은 중복을 허용한다.

    #step2: apikey를 발급받는다. apikeysms 8자리 숫자
    apikey = newApikey()
    print 'new apikey = %s' % apikey
    projectElement = Projects(owner_uid=userElement,apikey=apikey,name=name,platform=platform,stage=stage)
    projectElement.save();
    #step3: viwer db에 사용자와 프로젝트를 연결한다.
    Viewer.objects.create(uid=userElement,pid=projectElement)

    return HttpResponse('success registration')

def delete_req(request):
    try:
        user = User.objects.get(username__exact=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('%s not exists' % request.user)

    user.delete()

    return HttpResponse('delete success')

def so2sym(pid, appver, so_path, filename):
    arg = ['/google-breakpad/src/tools/linux/dump_syms/dump_syms' ,os.path.join(so_path,filename)]
    #arg = '/google-breakpad/src/tools/linux/dump_syms/dump_syms ' + os.path.join(so_path,filename)

    #fd_popen = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()

    if stderr.find('no debugging') != -1:
        print stderr
        return False

    vkey =  stdout.splitlines(False)[0].split()[3]

    sym_path = '/urqa/sympool/%s' % pid
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % appver
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    sym_path = sym_path + '/%s' % vkey
    if not os.path.isdir(sym_path):
        os.mkdir(sym_path)

    filename = filename + '.sym'
    fp = open(os.path.join(sym_path,filename) , 'wb')
    fp.write(stdout)
    fp.close()

    return True

def so_upload(request, pid):

    appver = request.POST['version']

    result, msg, userElement, projectElement = validUserPjt(request.user, pid)

    if not result:
        return HttpResponse(msg)

    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name
            path = '/urqa/sopool/%s' % pid
            if not os.path.isdir(path):
                os.mkdir(path)

            fp = open(os.path.join(path,filename) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()

            success_flag = so2sym(pid, appver, path, filename)
            if success_flag:
                return HttpResponse('File Uploaded, Valid so file')
            else:
                return HttpResponse('File Uploaded, but it have no debug info')
    return HttpResponse('Failed to Upload File')