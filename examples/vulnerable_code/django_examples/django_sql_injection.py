def handle(request):
    posts = Post.objects.order_by(request.GET["ordering"])
    return posts
