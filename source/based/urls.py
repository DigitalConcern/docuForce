"""based URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
import os

from django.contrib import admin
from django.urls import path, include
from web import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name='home'),
    path("programs", views.ProgramsPageView.as_view(), name='programs'),
    path("users", views.UsersPageView.as_view(), name='users'),
    path("programs/<int:pk>", views.ProgramsEditView.as_view(), name='update'),
    path("programs/<int:pk>/delete", views.ProgramsDeleteView.as_view(), name='delete'),
    path("programs/create", views.CreateProgView.as_view(), name='create'),
    path("admin/", admin.site.urls),
    path("users/<int:pk>", views.UsersEditView.as_view(), name='update2'),
    path("users/<int:pk>/delete", views.UsersDelView.as_view(), name='del2'),
    path("faq/<int:pk>", views.FAQView.as_view(), name='faqq'),

]
