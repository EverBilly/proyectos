from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime

# REST Framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

# Modelos y Serializadores
from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer
from rest_framework import generics, permissions

# ========== Helpers ==========
def validate_booking_times(start, end):
    """Valida que los horarios de reserva sean correctos"""
    if start >= end:
        return (False, "La hora de fin debe ser posterior a la de inicio")
    if start < datetime.now():
        return (False, "No se pueden crear reservas en el pasado")
    return (True, "")

def check_room_availability(room_id, start_time, end_time, booking_id=None):
    """Verifica si la sala está disponible en un horario específico"""
    query = Booking.objects.filter(
        room_id=room_id,
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    if booking_id:
        query = query.exclude(id=booking_id)
        
    return not query.exists()

# ========== Vistas HTML ==========
def home(request):
    """Vista principal redirige a dashboard si está autenticado"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """Vista de panel de control con paginación"""
    rooms = Room.objects.all()
    
    bookings = Booking.objects.select_related('room', 'user').order_by('-start_time')
    
    if not request.user.is_staff:
        bookings = bookings.filter(user=request.user)
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(bookings, 10)  # 10 items por página
    
    try:
        bookings_page = paginator.page(page)
    except PageNotAnInteger:
        bookings_page = paginator.page(1)
    except EmptyPage:
        bookings_page = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard.html', {
        'rooms': rooms,
        'bookings': bookings_page
    })

# ========== Autenticación ==========
@csrf_protect
def user_login(request):
    """Vista de inicio de sesión con validación mejorada"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        
        # Mejores mensajes de error
        for error in form.get_invalid_login_error():
            messages.error(request, error)
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@csrf_protect
def user_register(request):
    """Vista de registro con manejo mejorado de errores"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "¡Registro exitoso!")
            return redirect('dashboard')
            
        # Detalle de errores
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def user_logout(request):
    """Cierre de sesión seguro"""
    auth_logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect('home')

# ========== API Views ==========
@api_view(['GET', 'POST'])  # Asegúrate que acepta POST
@permission_classes([AllowAny])
def api_rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all().values('id', 'name', 'description', 'status')
        return Response({'data': list(rooms)})
    
    elif request.method == 'POST':
        # Asigna status='disponible' por defecto si no viene en request
        data = request.data.copy()
        if 'status' not in data:
            data['status'] = 'disponible'
            
        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_room_detail(request, pk):
    """API para gestionar salas individuales"""
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"error": "Solo administradores pueden editar salas"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"error": "Solo administradores pueden eliminar salas"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def api_bookings(request):
    if request.method == 'GET':
        bookings = Booking.objects.select_related('room').all()
        events = [{
            'id': b.id,
            'title': b.title,
            'start': b.start_time.isoformat(),
            'end': b.end_time.isoformat(),
            'room': b.room.name
        } for b in bookings]
        return Response(events)
    
    elif request.method == 'POST':
        serializer = BookingSerializer(data=request.data, context={'request': request})  # ¡Asegúrate de pasar el contexto!
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=201)  # Usa Response en lugar de JsonResponse para DRF
    return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_booking_detail(request, pk):
    """API para gestionar reservas individuales"""
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Verificar permisos
    if not request.user.is_staff and booking.user != request.user:
        return Response(
            {"error": "No tienes permiso para esta acción"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = BookingSerializer(booking)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = request.data.copy()
        data['user'] = booking.user.id  # Mantener el usuario original
        
        # Validación de horarios
        start_time = data.get('start_time', booking.start_time)
        end_time = data.get('end_time', booking.end_time)
        
        is_valid, error_msg = validate_booking_times(start_time, end_time)
        if not is_valid:
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar disponibilidad (excluyendo la reserva actual)
        if not check_room_availability(booking.room.id, start_time, end_time, booking.id):
            return Response(
                {"error": "La sala ya está reservada en ese horario"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BookingSerializer(booking, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)