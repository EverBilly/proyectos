from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator  # 👈 Nuevo

User = get_user_model()

class Room(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,  # 👈 Evita nombres duplicados
        validators=[MinLengthValidator(3)]  # 👈 Valida longitud mínima
    )
    description = models.TextField(
        max_length=500,  # 👈 Aumenté el límite para descripciones más completas
        blank=True  # 👈 Permite campo vacío
    )
    capacity = models.PositiveIntegerField()
    available_from = models.TimeField(default='10:00')
    available_to = models.TimeField(default='20:00')
    days_available = models.CharField(
        max_length=13,
        default="Lunes,Martes"
    )
    status = models.CharField(
        max_length=20,
        choices=[('disponible', 'Disponible'), ('ocupada', 'Ocupada'), ('mantenimiento', 'En Mantenimiento')],  # 👈 Opción adicional
        default='disponible',
        db_index=True  # 👈 Índice para búsquedas frecuentes
    )

    class Meta:
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'
        ordering = ['name']  # 👈 Orden default

    def __str__(self):
        return f"{self.name} ({self.get_status_display()}) (Capacidad: {self.capacity})"  # 👈 Muestra estado legible

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('aproved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings'  # 👈 Acceso inverso más claro
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Título del Evento'
    )
    start_time = models.DateTimeField(
        db_index=True  # 👈 Índice para búsquedas por fecha
    )
    end_time = models.DateTimeField()
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo de Contacto'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[MinLengthValidator(8)]  # 👈 Validación básica
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'  # 👈 Relación inversa
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True  # 👈 Índice para ordenamiento
    )

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-start_time']  # 👈 Orden descendente por defecto
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='check_end_time_after_start_time'  # 👈 Valida que end_time > start_time
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%d/%m/%Y')})"  # 👈 Formato fecha legible

