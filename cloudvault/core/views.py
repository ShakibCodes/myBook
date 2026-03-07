from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
import json
import mimetypes

from .models import User, Folder, File
from .forms import SignupForm, LoginForm, ProfileEditForm, FolderForm, FileUploadForm


# ─── Auth Views ───────────────────────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        errors = {field: errs[0] for field, errs in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    return render(request, 'core/auth.html', {'mode': 'signup'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return JsonResponse({'success': True, 'redirect': '/home/'})
            return JsonResponse({'success': False, 'errors': {'__all__': 'Invalid email or password.'}}, status=400)
        errors = {field: errs[0] for field, errs in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    return render(request, 'core/auth.html', {'mode': 'login'})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Home / File Manager Views ─────────────────────────────────────────────────

@login_required
def home_view(request):
    folder_id = request.GET.get('folder')
    current_folder = None
    breadcrumb = []

    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
        breadcrumb = current_folder.get_path()
        folders = current_folder.subfolders.all()
        files = current_folder.files.all()
    else:
        folders = Folder.objects.filter(owner=request.user, parent=None)
        files = []

    return render(request, 'core/home.html', {
        'folders': folders,
        'files': files,
        'current_folder': current_folder,
        'breadcrumb': breadcrumb,
    })


@login_required
@require_POST
def create_folder(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    parent_id = data.get('parent_id')
    visibility = data.get('visibility', 'private')
    color = data.get('color', '#6366f1')

    if not name:
        return JsonResponse({'success': False, 'error': 'Name is required'}, status=400)

    parent = None
    if parent_id:
        parent = get_object_or_404(Folder, id=parent_id, owner=request.user)

    folder = Folder.objects.create(
        owner=request.user,
        name=name,
        parent=parent,
        visibility=visibility,
        color=color,
    )
    return JsonResponse({
        'success': True,
        'folder': {
            'id': str(folder.id),
            'name': folder.name,
            'visibility': folder.visibility,
            'color': folder.color,
            'created_at': folder.created_at.strftime('%b %d, %Y'),
            'items': 0,
        }
    })


@login_required
@require_POST
def rename_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
    folder.name = name
    folder.save()
    return JsonResponse({'success': True, 'name': folder.name})


@login_required
@require_POST
def update_folder_visibility(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    data = json.loads(request.body)
    visibility = data.get('visibility')
    if visibility in ['public', 'private']:
        folder.visibility = visibility
        folder.save()
        return JsonResponse({'success': True, 'visibility': folder.visibility})
    return JsonResponse({'success': False, 'error': 'Invalid visibility'}, status=400)


@login_required
@require_POST
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def upload_file(request):
    folder_id = request.POST.get('folder_id')
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'success': False, 'error': 'No file'}, status=400)

    file_obj = File.objects.create(
        folder=folder,
        name=uploaded_file.name,
        file=uploaded_file,
        file_size=uploaded_file.size,
        mime_type=uploaded_file.content_type or '',
    )
    return JsonResponse({
        'success': True,
        'file': {
            'id': str(file_obj.id),
            'name': file_obj.name,
            'size': file_obj.get_size_display(),
            'icon': file_obj.get_icon(),
            'is_image': file_obj.is_image(),
            'url': file_obj.file.url if file_obj.file else '',
            'created_at': file_obj.created_at.strftime('%b %d, %Y'),
        }
    })


@login_required
@require_POST
def rename_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id, folder__owner=request.user)
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
    file_obj.name = name
    file_obj.save()
    return JsonResponse({'success': True, 'name': file_obj.name})


@login_required
@require_POST
def delete_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id, folder__owner=request.user)
    if file_obj.file:
        try:
            file_obj.file.delete(save=False)
        except:
            pass
    file_obj.delete()
    return JsonResponse({'success': True})


@login_required
def download_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)
    # Check access
    if file_obj.folder.owner != request.user:
        if not file_obj.folder.is_accessible_by(request.user):
            raise Http404
    response = HttpResponse(file_obj.file, content_type=file_obj.mime_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
    return response


# ─── Explore / Search Views ────────────────────────────────────────────────────

@login_required
def explore_view(request):
    query = request.GET.get('q', '').strip()
    users = []
    if query:
        users = User.objects.filter(
            Q(email__icontains=query) | Q(username__icontains=query)
        ).exclude(id=request.user.id).filter(is_active=True)[:20]
    return render(request, 'core/explore.html', {'users': users, 'query': query})


@login_required
def user_profile_public(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, is_active=True)
    if profile_user == request.user:
        return redirect('profile')

    folder_id = request.GET.get('folder')
    current_folder = None
    breadcrumb = []

    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, owner=profile_user)
        # Only allow if accessible
        if not current_folder.is_accessible_by(request.user):
            raise Http404
        breadcrumb = current_folder.get_path()
        folders = current_folder.subfolders.filter(visibility='public')
        files = current_folder.files.all()
    else:
        folders = Folder.objects.filter(owner=profile_user, parent=None, visibility='public')
        files = []

    folder_count = Folder.objects.filter(owner=profile_user, parent=None, visibility='public').count()

    return render(request, 'core/user_public.html', {
        'profile_user': profile_user,
        'folders': folders,
        'files': files,
        'current_folder': current_folder,
        'breadcrumb': breadcrumb,
        'folder_count': folder_count,
    })


# ─── Profile Views ─────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {'profile_user': request.user})


@login_required
@require_POST
def update_profile(request):
    form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'Profile updated!'})
    errors = {field: errs[0] for field, errs in form.errors.items()}
    return JsonResponse({'success': False, 'errors': errors}, status=400)


@login_required
@require_POST
def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    return JsonResponse({'success': True, 'redirect': '/login/'})


# ─── API: Get folder contents ──────────────────────────────────────────────────

@login_required
def folder_contents(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    subfolders = [{
        'id': str(f.id),
        'name': f.name,
        'visibility': f.visibility,
        'color': f.color,
        'items': f.get_all_items_count(),
        'created_at': f.created_at.strftime('%b %d, %Y'),
    } for f in folder.subfolders.all()]
    files = [{
        'id': str(f.id),
        'name': f.name,
        'size': f.get_size_display(),
        'icon': f.get_icon(),
        'is_image': f.is_image(),
        'url': f.file.url if f.file else '',
        'created_at': f.created_at.strftime('%b %d, %Y'),
    } for f in folder.files.all()]
    return JsonResponse({'folders': subfolders, 'files': files})
