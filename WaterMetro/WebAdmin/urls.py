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

from django.urls import path
from WebAdmin import views
app_name = "WebAdmin"

urlpatterns = [
    path('Homepage/',views.homepage,name='Homepage'),
    path('District/', views.district, name='District'),
    path('Toggle_Status/<int:did>', views.toggle_status, name='Toggle_Status'),
    path('Place/', views.place, name='Place'),
    path('Toggle_Place_Status/<int:pid>', views.toggle_place_status, name='Toggle_Place_Status'),
    path('EventType/', views.event_type, name='EventType'),
    path('Update_Eventtype/<int:did>', views.update_eventtype, name='Update_Eventtype'),
    path('Toggle_Eventtype_Status/<int:did>', views.toggle_eventtype_status, name='Toggle_Eventtype_Status'),
    path('StationMasterRegistration/', views.stationmaster_registration, name='StationMaster_Registration'),
    path('StationMasterList/', views.station_master_list, name='StationMasterList'),
    path('ToggleStationMasterStatus/', views.toggle_station_master_status, name='ToggleStationMasterStatus'),
    path('Boat/', views.boat, name='Boat'),
    path('Update_Boat/<int:did>', views.update_boat, name='Update_Boat'),
    path('Toggle_Boat_Status/<int:did>', views.toggle_boat_status, name='Toggle_Boat_Status'),
    path('Report/',views.report,name="Report"),
    path('ajaxreport/',views.ajaxreport,name="AjaxReport"),
]
