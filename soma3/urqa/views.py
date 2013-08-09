# Create your views here.
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

def index(request):
#	return HttpResponse('hello world')
	tpl = loader.get_template('test.html')
	ctx = Context({});
	return HttpResponse(tpl.render(ctx))
	#return HttpResponse('awefawefawefawef')

@csrf_exempt
def adduser(request):

	print request
	#print request.POST['email']
	#print request.POST['passwd']
	#print request.POST['nick']
	#print request.POST['company']
	
	str = request.POST['email']# + request.POST['passwd'] + request.POST['nick'] + request.POST['company']
	#request.
	return HttpResponse('hello world ' + str);

def posttest(request):	
	c = {} 
	return render(request,'posttestmodule.html',c)
