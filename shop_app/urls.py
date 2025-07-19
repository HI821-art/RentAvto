from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user.views import CustomLoginView, profile_view, CustomLogoutView, register_view, edit_profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('car.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)