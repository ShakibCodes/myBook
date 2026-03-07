from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Main sections
    path('home/', views.home_view, name='home'),
    path('explore/', views.explore_view, name='explore'),
    path('profile/', views.profile_view, name='profile'),

    # Folder operations
    path('api/folders/create/', views.create_folder, name='create_folder'),
    path('api/folders/<uuid:folder_id>/rename/', views.rename_folder, name='rename_folder'),
    path('api/folders/<uuid:folder_id>/visibility/', views.update_folder_visibility, name='update_folder_visibility'),
    path('api/folders/<uuid:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('api/folders/<uuid:folder_id>/contents/', views.folder_contents, name='folder_contents'),

    # File operations
    path('api/files/upload/', views.upload_file, name='upload_file'),
    path('api/files/<uuid:file_id>/rename/', views.rename_file, name='rename_file'),
    path('api/files/<uuid:file_id>/delete/', views.delete_file, name='delete_file'),
    path('api/files/<uuid:file_id>/download/', views.download_file, name='download_file'),

    # Profile
    path('api/profile/update/', views.update_profile, name='update_profile'),
    path('api/profile/delete/', views.delete_account, name='delete_account'),

    # Public user profile
    path('u/<uuid:user_id>/', views.user_profile_public, name='user_public'),
]
