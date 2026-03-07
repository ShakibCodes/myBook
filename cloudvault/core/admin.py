from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Folder, File


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'date_joined', 'is_active']
    list_filter = ['is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('username', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
    search_fields = ['email', 'username']
    ordering = ['-date_joined']


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'visibility', 'parent', 'created_at']
    list_filter = ['visibility']
    search_fields = ['name', 'owner__email']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'folder', 'file_size', 'created_at']
    search_fields = ['name']
