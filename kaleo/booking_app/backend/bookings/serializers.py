from rest_framework import serializers
from django.utils.timezone import now
from .models import Room, Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'status']

class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.ReadOnlyField(source='room.name')

    class Meta:
        model = Booking
        fields = ['id', 'room', 'room_name', 'title', 'start_time', 'end_time', 'email', 'phone', 'user', 'created_at']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la de fin")
        if data['start_time'] < now():
            raise serializers.ValidationError("No se pueden crear citas en el pasado")
        return data