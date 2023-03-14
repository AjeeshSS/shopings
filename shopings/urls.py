
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin1/', admin.site.urls),
    path('', include('app.urls')),
    path('admin/', include('adminapp.urls')),
    
]

handler404 = "app.views.handle_not_found"
