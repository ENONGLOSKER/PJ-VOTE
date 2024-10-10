"""
URL configuration for vote_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from vote_app import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # auth
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/register/', views.user_register, name='user_register'),
    # user
    path('', views.get_started, name='get_started'),
    path('vote/', views.vote_list, name='vote_list'),
    path('vote/add/', views.create_vote, name='create_vote'),
    path('vote/<int:vote_id>/', views.vote_detail, name='vote_detail'),
    path('vote/like/<int:vote_id>/', views.like_vote, name='like_vote'),
    path('vote/access/<int:vote_id>/', views.access_vote, name='access_vote'),
    path('vote/add_options/<int:vote_id>/', views.add_options, name='add_options'),
    path('vote/<int:vote_id>/add_option/admin/', views.add_option_admin, name='add_option_admin'),
    # admin
    path('vote/admin/', views.admin_vote_list, name='admin_vote_list'),
    path('vote/edit/<int:vote_id>/', views.edit_vote, name='edit_vote'),
    path('delete-vote/<int:vote_id>/', views.delete_vote, name='delete_vote'),
    path('vote/option/admin/', views.admin_vote_option, name='admin_vote_option'),
    path('vote/<int:vote_id>/options/', views.admin_vote_option, name='admin_vote_option'),
    path('option/<int:option_id>/edit/', views.edit_option, name='edit_option'),
    path('option/<int:option_id>/delete/', views.delete_option, name='delete_option'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)