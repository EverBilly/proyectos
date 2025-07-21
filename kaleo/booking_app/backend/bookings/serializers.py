from rest_framework import serializers
from django.utils.timezone import now
from .models import Room, Booking
from datetime import timedelta
from django.core.exceptions import ValidationError

class RoomSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'description', 'status', 'status_display']
        read_only_fields = ['status_display']
        extra_kwargs = {
            'status': {'help_text': "Estado actual de la habitación (disponible/ocupada)"}
        }

class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    duration = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'room', 'room_name', 'title', 
            'start_time', 'end_time', 'duration', 'is_active',
            'email', 'phone', 'user', 'user_email', 'created_at'
        ]
        read_only_fields = ['created_at', 'room_name', 'user_email']
        extra_kwargs = {
            'room': {'required': True},
            'user': {'read_only': True}
        }

    def get_duration(self, obj):
        """Calcula la duración en horas"""
        return round((obj.end_time - obj.start_time).total_seconds() / 3600, 2)

    def get_is_active(self, obj):
        """Indica si la reserva está en curso"""
        return obj.start_time <= now() <= obj.end_time

    def validate(self, data):
        # Validación básica de fechas
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({
                'end_time': "Debe ser posterior a la fecha de inicio"
            })

        if data['start_time'] < now():
            raise serializers.ValidationError({
                'start_time': "No se pueden crear reservas en el pasado"
            })

        # Validación de duración máxima (4 horas)
        max_duration = timedelta(hours=4)
        if (data['end_time'] - data['start_time']) > max_duration:
            raise serializers.ValidationError({
                'end_time': f"La reserva no puede exceder {max_duration.seconds/3600} horas"
            })

        # Validación de horario comercial (8am-8pm)
        start_hour = data['start_time'].time().hour
        end_hour = data['end_time'].time().hour
        if not (8 <= start_hour < 20) or not (8 < end_hour <= 20):
            raise serializers.ValidationError({
                'start_time': "Las reservas solo están disponibles entre 8am y 8pm"
            })

        return data

    def create(self, validated_data):
        # Asignación automática del usuario autenticado
        validated_data['user'] = self.context['request'].user
        
        # Validación adicional de disponibilidad
        room = validated_data['room']
        if room.status != 'disponible':
            raise ValidationError({"room": "La habitación no está disponible"})
        
        return super().create(validated_data)

# Serializador para generación de PDFs
class BookingPDFSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)
    formatted_date = serializers.SerializerMethodField()
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'title', 'formatted_date', 
            'room_details', 'qr_code'
        ]

    def get_formatted_date(self, obj):
        return {
            'start': obj.start_time.strftime('%d/%m/%Y %H:%M'),
            'end': obj.end_time.strftime('%d/%m/%Y %H:%M'),
            'duration': self.get_duration(obj)
        }