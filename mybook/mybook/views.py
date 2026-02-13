from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import User



def signup_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        cp_word = request.POST.get('cpassword')

        if p_word == cp_word:
            # Create user and log them in
            user = User.objects.create_user(username=u_name, password=p_word)
            auth_login(request, user)
            # Rule 3: New registers go to setup
            return redirect('setup') 
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            auth_login(request, user)
            # Rule 2: Existing accounts go to home
            return redirect('home') 
    return render(request, "login.html")

@login_required
def setup_view(request):
    if request.method == "POST":
        user = request.user
        user.display_name = request.POST.get('display-name')
        user.about = request.POST.get('about')
        if 'profile-photo' in request.FILES:
            user.profile_photo = request.FILES['profile-photo']
        user.save()
        return redirect('home')
    return render(request, "setup.html")

@login_required
def home_view(request):
    # Rule 1: Non-logged users are restricted by @login_required
    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect('login')

login_required
def edit_profile_view(request):
    user = request.user
    if request.method == "POST":
        user.display_name = request.POST.get('display_name')
        user.about = request.POST.get('about')
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        return redirect('home')
    return render(request, "edit_profile.html")


@login_required
def profile(request):
    return render(request, "profile.html")



# task:
# home.html => profile.html
# new home.html