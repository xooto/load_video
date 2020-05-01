from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import url
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='static/favicon.ico'), name='favicon'),
    path('', views.index),
    path('infoVideo/', views.info),
    path('video/', views.creat),
    path('get/', views.chunkGet),
]
