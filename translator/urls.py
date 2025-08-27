"""
URLs pour l'application translator
Projet créé par Marino ATOHOUN
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('process_camera/', views.process_camera, name='process_camera'),
    path('process_url/', views.process_url, name='process_url'),
    path('api/model_info/', views.get_model_info, name='model_info'),
    path('api/recent_results/', views.get_recent_results, name='recent_results'),
    path('about/', views.about, name='about'),
    path('documentation/', views.documentation, name='documentation'),
    path('contact/', views.contact, name='contact'),
]

