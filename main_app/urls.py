from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('albums/', views.album_index, name='album-index'),
    path('albums/<slug:album_slug>/', views.album_detail, name='album_detail'),
    path('albums/<slug:album_slug>/comments/create/', views.comment_create, name='comment_create'),
    path('comments/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('comment/<int:comment_id>/like/', views.toggle_like, name='toggle_like'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='home.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]