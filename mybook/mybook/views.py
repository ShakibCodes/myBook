from django.shortcuts import render

def login(request):
    return render(request, "index.html")

def signup(request):
    return render(request, "signup.html")


def setup(request):
    return render(request, "setup.html")