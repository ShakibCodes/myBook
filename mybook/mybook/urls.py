from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # AUTH
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('setup/', views.setup_view, name='setup'),

    # Home ROOT
    path('', views.home_view, name='home'),
    
    # CONTENT & PROFILE
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('folder/<int:folder_id>/', views.folder_detail_view, name='folder_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)