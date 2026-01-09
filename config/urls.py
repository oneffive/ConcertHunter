from django.contrib import admin
from django.urls import path, include  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('events.urls')), 
    path('delete/<int:sub_id>/', views.delete_subscription, name='delete_subscription'), 
]