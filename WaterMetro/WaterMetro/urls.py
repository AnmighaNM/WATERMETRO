"""
URL configuration for WaterMetro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from Guest import views as guest_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('WebAdmin/',include(('WebAdmin.urls', 'WebAdmin'), namespace='WebAdmin')),
    path('Guest/',include(('Guest.urls', 'WebGuest'), namespace='WebGuest')),
    path('StationMaster/',include(('StationMaster.urls', 'WebStationMaster'), namespace='WebStationMaster')),
    path('User/', include(('User.urls', 'WebUser'), namespace='WebUser')),
    # path('', guest_views.Index, name='index'), # Set the root URL to the index view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)