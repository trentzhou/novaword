from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

def index(request):
    return render(request, 'index.html')
