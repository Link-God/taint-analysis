from django.shortcuts import render


def my_render(req):
    return render(req, 'some_template.html')
