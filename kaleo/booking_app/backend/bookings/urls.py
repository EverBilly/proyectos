from django.urls import path
from bookings.views import api_rooms, api_room_detail, api_bookings, api_booking_detail

urlpatterns = [
    path('rooms/', api_rooms, name='api_rooms'),
    path('rooms/<int:pk>/', api_room_detail, name='api_room_detail'),
    path('bookings/', api_bookings, name='api_bookings'),
    path('bookings/<int:pk>/', api_booking_detail, name='api_booking_detail'),
]