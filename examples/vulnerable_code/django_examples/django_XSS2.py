from .some_taint_file import my_render


def xss2(request):
    return my_render(request)
