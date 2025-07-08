from django.urls import path
from . import views

urlpatterns = [
    path('api/rooms/', views.api_rooms),
    path('api/rooms/<int:pk>/', views.api_room_detail),

    path('api/bookings/', views.api_bookings),
    path('api/bookings/<int:pk>/', views.api_booking_detail),
]