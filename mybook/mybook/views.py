from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import User, Folder, File

#AUTHENTICATION

def signup_view(request):
   # No seeing login if regd
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        cp_word = request.POST.get('cpassword')

        if p_word == cp_word:
            user = User.objects.create_user(username=u_name, password=p_word)
            auth_login(request, user)
            request.session['is_new_user'] = True
            return redirect('setup') 
    return render(request, "signup.html")

def login_view(request):
    # No seeing login if he see already logged in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            auth_login(request, user)
            return redirect('home') 
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

#PROFILE & SETUP

@login_required
def setup_view(request):
    # strict reachable after reg
    if not request.session.get('is_new_user'):
        return redirect('home')

    if request.method == "POST":
        user = request.user
        user.display_name = request.POST.get('display-name')
        user.about = request.POST.get('about')
        if 'profile-photo' in request.FILES:
            user.profile_photo = request.FILES['profile-photo']
        user.save()
  
        del request.session['is_new_user']
        return redirect('home')
    return render(request, "setup.html")

@login_required
def profile_view(request):
    return render(request, "profile.html")

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == "POST":
        user.display_name = request.POST.get('display_name')
        user.about = request.POST.get('about')
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        return redirect('profile')
    return render(request, "edit_profile.html")

# ROOT

@login_required
def home_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Folder.objects.create(user=request.user, name=name, description=description)
        return redirect('home')

    query = request.GET.get('q')
    folders = Folder.objects.filter(user=request.user)
    if query:
        folders = folders.filter(name__icontains=query)

    return render(request, "home.html", {'folders': folders})

@login_required
def folder_detail_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == "POST":
        files = request.FILES.getlist('files')
        for f in files:
            File.objects.create(folder=folder, file=f)
        return redirect('folder_detail', folder_id=folder.id)

    files = folder.files.all()
    return render(request, "folder_detail.html", {'folder': folder, 'files': files})

@login_required
def delete_folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == "POST":
        folder.delete()
        return redirect('home')
    return redirect('home')