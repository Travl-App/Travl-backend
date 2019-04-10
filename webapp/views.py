from django.shortcuts import render


def index_view(request):
    return render(request, 'webapp/index.html', context={})


def article_view(request, key):
    assert key
    return render(request, 'webapp/index.html', context={})


def place_view(request, key):
    assert key
    return render(request, 'webapp/index.html', context={})
