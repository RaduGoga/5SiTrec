from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('materii/', views.materii_list, name='materii'),
    path('materii/<int:pk>/delete/', views.materie_delete, name='materie_delete'),
    path('note/', views.note_list, name='note'),
    path('note/<int:pk>/delete/', views.nota_delete, name='nota_delete'),
    path('absente/', views.absente_list, name='absente'),
    path('absente/<int:pk>/delete/', views.absenta_delete, name='absenta_delete'),
    path('checkin/', views.checkin_view, name='checkin'),
    path('reflectii/', views.reflectii_list, name='reflectii'),
]
