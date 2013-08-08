# Create your views here.
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader

def index(request):
#	return HttpResponse('hello world')
	tpl = loader.get_template('test.html')
	ctx = Context({});
	return HttpResponse(tpl.render(ctx))
