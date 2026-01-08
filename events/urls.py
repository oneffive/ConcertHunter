from django.urls import path
from . import views

urlpatterns = [
    path('', views.artist_search, name='search'),
    path('subscribe/<str:tm_id>/', views.subscribe, name='subscribe'),
]