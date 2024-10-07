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
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/register/', views.user_register, name='user_register'),


    path('like/<int:vote_id>/', views.like_vote, name='like_vote'),
    path('create/', views.create_vote, name='create_vote'),
    path('add_options/<int:vote_id>/', views.add_options, name='add_options'),
    path('access/<int:vote_id>/', views.access_vote, name='access_vote'),
    path('vote/<int:vote_id>/', views.vote_detail, name='vote_detail'),
    path('vote', views.vote_list, name='vote_list'),
    path('', views.get_started, name='get_started'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)