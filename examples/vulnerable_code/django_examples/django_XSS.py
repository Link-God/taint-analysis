from django.shortcuts import render


def xss1(request):
    return render(request, 'templates/xss.html')
