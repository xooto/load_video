from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('infoVideo/', views.info),
    path('video/', views.creat),
    path('get/', views.chunkGet),
]
