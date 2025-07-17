from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Room, Booking

# ====================== CUSTOM FILTERS ======================
class AvailabilityFilter(admin.SimpleListFilter):
    title = 'Disponibilidad'
    parameter_name = 'availability'

    def lookups(self, request, model_admin):
        return [
            ('available', 'Disponibles'),
            ('occupied', 'Ocupadas'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'available':
            return queryset.filter(status='disponible')
        if self.value() == 'occupied':
            return queryset.filter(status='ocupada')

# ====================== ROOM ADMIN ======================
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status_badge', 'booking_count', 'actions_column')
    list_filter = (AvailabilityFilter,)  # Usamos nuestro filtro personalizado
    search_fields = ('name', 'description')
    list_per_page = 20

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description')
        }),
        ('Estado', {
            'fields': ('status',),
            'description': 'Estado actual de la habitación'
        }),
    )

    # ---- Métodos personalizados ----
    def status_badge(self, obj):
        colors = {
            'disponible': 'green',
            'ocupada': 'red',
            'mantenimiento': 'orange'
        }
        return format_html(
            '<span class="badge" style="background-color: {}; color: white; padding: 3px 8px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def booking_count(self, obj):
        count = obj.bookings.count()
        url = (
            reverse('admin:bookings_booking_changelist')
            + f'?room__id__exact={obj.id}'
        )
        return format_html('<a href="{}">{} reservas</a>', url, count)
    booking_count.short_description = 'Reservas'

    def actions_column(self, obj):
        return format_html(
            '<div class="nowrap">'
            '<a class="button" href="{}/change/">Editar</a>&nbsp;'
            '<a class="button" href="{}/delete/">Eliminar</a>'
            '</div>',
            obj.id, obj.id
        )
    actions_column.short_description = 'Acciones'
    actions_column.allow_tags = True

# ====================== BOOKING ADMIN ======================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event_title',
        'room_link',
        'date_range',
        'user_with_link',
        'user',
        'contact_quick_info',
        'created_at_formatted'
    )
    list_filter = (
        'room',
        ('start_time', admin.DateFieldListFilter),
    )
    search_fields = ('title', 'room__name', 'user__email', 'phone')
    date_hierarchy = 'start_time'
    readonly_fields = ('created_at',)
    list_select_related = ('room', 'user')

    fieldsets = (
        ('Detalles del Evento', {
            'fields': ('title', 'room', 'user')
        }),
        ('Horario', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',)
        }),
        ('Información de Contacto', {
            'fields': ('email', 'phone'),
            'classes': ('wide',)
        }),
    )

    # ---- Métodos personalizados ----
    def event_title(self, obj):
        return format_html('<strong>{}</strong>', obj.title)
    event_title.short_description = 'Evento'

    def room_link(self, obj):
        url = reverse('admin:bookings_room_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room)
    room_link.short_description = 'Habitación'

    def date_range(self, obj):
        return format_html(
            '{}<br><strong>a</strong><br>{}',
            obj.start_time.strftime('%d/%m/%Y %H:%M'),
            obj.end_time.strftime('%d/%m/%Y %H:%M')
        )
    date_range.short_description = 'Fecha/Hora'

    def user_with_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.email)
        return "-"
    user_with_link.short_description = 'Usuario'

    def contact_quick_info(self, obj):
        return format_html(
            '📧 {}<br>📞 {}',
            obj.email or '--',
            obj.phone or '--'
        )
    contact_quick_info.short_description = 'Contacto'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
    created_at_formatted.short_description = 'Creado'
    created_at_formatted.admin_order_field = 'created_at'

# Personalización del sitio admin
admin.site.site_header = "Kaleo Admin"
admin.site.site_title = "Sistema de Gestión de Reservas"
admin.site.index_title = "Bienvenido al Panel de Control"