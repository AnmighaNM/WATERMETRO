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
from StationMaster import views
app_name = "WebStationMaster"

urlpatterns = [
   path('HomePage/',views.homepage,name='HomePage'),
    path('MyProfile/',views.myprofile,name='MyProfile'),
    path('EditProfile/',views.editprofile,name='EditProfile'),
    path('assign_boat/', views.assign_boat, name='assign_boat'),
    path('get_active_boats/',views.get_active_boats, name='get_active_boats'),
    path('Services/', views.services, name='Services'),
    path('Update_Service/<int:did>', views.update_service, name='Update_Service'),
    path('Toggle_Service_Status/<int:did>', views.toggle_service_status, name='Toggle_Service_Status'),
    path('View_Services/', views.view_services, name='View_Services'),
    path('ViewEventBooking/',views.vieweventbooking,name='vieweventbooking'),
    path('ViewTicketBooking/',views.viewticketbooking,name='ViewTicketBooking'),
    path('initiate_refund/', views.initiate_refund, name='initiate_refund'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('refund/', views.refund, name='refund'),
    path('callback/', views.callback, name='callback'),
    path('ViewComplaint/',views.viewcomplaints,name='ViewComplaint'),
    path('Reply/<int:did>',views.reply,name='Reply'),
    path('RepliedComplaints/',views.repliedcomplaints,name='RepliedComplaints'),
    path('ChangePassword/',views.changepassword,name='ChangePassword'),
    path('Report/',views.report,name="Report"),
    path('ajaxreport/',views.ajaxreport,name="AjaxReport"),
]
