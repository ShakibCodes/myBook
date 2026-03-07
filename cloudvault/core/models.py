from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import os
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'avatars/{instance.id}.{ext}'


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True, max_length=300)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_display_name(self):
        return self.username if self.username else self.email.split('@')[0]

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def get_public_folders_count(self):
        return self.folders.filter(parent=None, visibility='public').count()

    def get_total_folders_count(self):
        return self.folders.filter(parent=None).count()

    def __str__(self):
        return self.email


class Folder(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=7, default='#6366f1')

    class Meta:
        ordering = ['name']

    def get_all_items_count(self):
        files = self.files.count()
        folders = self.subfolders.count()
        return files + folders

    def get_path(self):
        path = [self]
        parent = self.parent
        while parent:
            path.insert(0, parent)
            parent = parent.parent
        return path

    def is_accessible_by(self, user):
        if self.owner == user:
            return True
        # Check if root or any ancestor is public
        current = self
        while current:
            if current.visibility == 'public':
                return True
            current = current.parent
        return False

    def __str__(self):
        return f"{self.owner.get_display_name()}/{self.name}"


def file_upload_path(instance, filename):
    return f'files/{instance.folder.owner.id}/{uuid.uuid4()}_{filename}'


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=file_upload_path)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def get_size_display(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        return f"{size/(1024*1024*1024):.1f} GB"

    def get_icon(self):
        ext = self.name.split('.')[-1].lower() if '.' in self.name else ''
        icons = {
            'pdf': 'file-text', 'doc': 'file-text', 'docx': 'file-text', 'txt': 'file-text',
            'xls': 'file-spreadsheet', 'xlsx': 'file-spreadsheet', 'csv': 'file-spreadsheet',
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'webp': 'image', 'svg': 'image',
            'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video',
            'mp3': 'music', 'wav': 'music', 'flac': 'music',
            'zip': 'archive', 'rar': 'archive', 'tar': 'archive', 'gz': 'archive',
            'py': 'code', 'js': 'code', 'html': 'code', 'css': 'code', 'json': 'code',
        }
        return icons.get(ext, 'file')

    def is_image(self):
        ext = self.name.split('.')[-1].lower() if '.' in self.name else ''
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']

    def __str__(self):
        return self.name
