# coding=utf-8
from functools import wraps
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string


def render_to(template=None, output='response', mimetype=None):
    """ 
    Decorator for Django views that sends returned dict to render_to_response
    function.

    Source: https://bitbucket.org/offline/django-annoying/src/ -> annoying/decorators.py

    Template name can be decorator parameter or TEMPLATE item in returned
    dictionary.  RequestContext always added as context instance.
    If view doesn't return dict then decorator simply returns output.

    Important: The first parameter of the being-wrapped function must be a request object!

    Parameters:
     - template: template name to use
     - output: output type. can be 'response' or 'string'. default 'response'.
               note that setting the mime type does not work when using a
               string response.
     - mimetype: content type to send in response headers

    Examples:
    # 1. Template name in decorator parameters

    @render_to('template.html')
    def foo(request):
        bar = Bar.object.all()
        return {'bar': bar}

    # equals to
    def foo(request):
        bar = Bar.object.all()
        return render_to_response('template.html',
                                  {'bar': bar},
                                  context_instance=RequestContext(request))


    # 2. Template name as TEMPLATE item value in return dictionary.
         if TEMPLATE is given then its value will have higher priority
         than render_to argument.

    @render_to()
    def foo(request, category):
        template_name = '%s.html' % category
        return {'bar': bar, 'TEMPLATE': template_name}

    #equals to
    def foo(request, category):
        template_name = '%s.html' % category
        return render_to_response(template_name,
                                  {'bar': bar},
                                  context_instance=RequestContext(request))

    """
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output_func = function(request, *args, **kwargs)
            if not isinstance(output_func, dict):
                return output_func
            tmpl = output_func.pop('TEMPLATE', template)

            if output == 'response':
                return render_to_response(tmpl, output_func, \
                            context_instance=RequestContext(request), mimetype=mimetype)
            elif output == 'string':
                return render_to_string(tmpl, output_func, \
                            context_instance=RequestContext(request))
            else:
                raise ValueError('Invalid output type.')

        return wrapper
    return renderer
