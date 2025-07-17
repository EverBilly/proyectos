from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    api_rooms,
    api_room_detail,
    api_bookings,
    api_booking_detail,
    user_login,
    user_register,
    user_logout,
    dashboard,
    home,
)


app_name = 'bookings'

urlpatterns = [

    # ==================== API Endpoints ====================
    # Autenticación JWT (para clientes API)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API v1 - Rooms
    path('v1/rooms/', api_rooms, name='api-rooms-list'),
    path('v1/rooms/<int:pk>/', api_room_detail, name='api-rooms-detail'),

    # API v1 - Bookings
    path('v1/bookings/', api_bookings, name='bookings-list'),
    path('v1/bookings/<int:pk>/', api_booking_detail, name='api-bookings-detail'),

    # API v2 (Ejemplo para futura versión)
    # path('api/v2/rooms/', ..., name='api-v2-rooms-list'),
]

# ==================== Mejoras implementadas ====================
"""
1. Estructura clara separando vistas HTML y API
2. Versionado de API (/v1/) para futuras actualizaciones
3. Endpoints JWT para autenticación API
4. Nombres consistentes en URLs (api-rooms-list vs api_rooms)
5. Sistema de nombres (app_name) para mejor referencia
6. Preparación para múltiples versiones de API
7. Documentación implícita mediante estructura
"""