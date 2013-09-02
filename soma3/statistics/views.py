# Create your views here.
# -*- coding: utf-8 -*-

from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect

def statistics(request,pid):
    tpl = loader.get_template('statistics.html')
    ctx = Context({});
    return HttpResponse(tpl.render(ctx))