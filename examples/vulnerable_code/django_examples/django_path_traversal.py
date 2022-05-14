import os


def path_traversal(request):
    image = os.path.join("root", "images", request.POST["some_param"])
    return image
