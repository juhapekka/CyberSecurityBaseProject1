from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_note, name='add_note'),
    path('login/', views.custom_login, name='custom_login'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('search/', views.search_notes, name='search_notes'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
]