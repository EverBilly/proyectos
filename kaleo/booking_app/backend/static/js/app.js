// ========== Variables Globales ==========
const API_URL = '/api/v1/bookings/';
const API_BASE = '/api/v1/';

const csrftoken = getCookie('csrftoken');
let calendar = null;
let bookingModal = null;
let currentRoomId = null;

// ========== Funciones Básicas ==========
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(`${name}=`)) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para agregar sala
async function addRoom() {
    const name = document.getElementById('room-name').value;
    const description = document.getElementById('room-description').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch('/api/v1/rooms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'  // Importante para Django
            },
            body: JSON.stringify({
                name: name,
                description: description,
                status: 'disponible'  // Asegura que el status esté presente
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error al crear sala');
        }
        
        showNotification('Sala creada exitosamente!');
        loadRooms();
        document.getElementById('room-form').reset();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Error al crear sala', 'danger');
    }
}

function showNotification(message, type = "success") {
    const notification = document.getElementById("notification");
    if (!notification) return;

    notification.textContent = message;
    notification.className = `alert alert-${type} fixed-top w-100 text-center`;
    notification.classList.remove("d-none");

    setTimeout(() => {
        notification.classList.add("d-none");
    }, 3000);
}

// ========== Funciones de Calendario ==========
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: {
            url: `${API_BASE}bookings/`,
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrftoken
            },
            failure: function(error) {
                console.error('Error cargando eventos:', error);
                // Muestra error sin redireccionar
                alert('Error al cargar eventos. Intenta recargar la página.');
            }
        },
        eventClick: function(info) {
            if (confirm(`¿Eliminar evento "${info.event.title}"?`)) {
                deleteBooking(info.event.id);
            }
        },
        dateClick: function(info) {
            openBookingModal(info.dateStr);
        }
    }).render();
}

function refreshCalendar() {
    if (calendar) {
        calendar.refetchEvents();
    }
}

// ========== Funciones de Reservas ==========
function deleteBooking(bookingId) {
    fetch(`${API_URL}${bookingId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error al eliminar');
        showNotification('Reserva eliminada', 'success');
        refreshCalendar();
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al eliminar reserva', 'danger');
    });
}

function openBookingModal(dateStr, roomId = null) {
    if (!bookingModal) return;

    const now = new Date();
    now.setHours(now.getHours() + 1);
    const minDate = now.toISOString().slice(0, 16);

    const roomInput = document.getElementById("booking-room-id");
    if (roomInput && roomId) {
        roomInput.value = roomId;
        currentRoomId = roomId;
    }

    document.getElementById('booking-start').min = minDate;
    document.getElementById('booking-end').min = minDate;
    document.getElementById('booking-start').value = dateStr + 'T09:00';
    document.getElementById('booking-end').value = dateStr + 'T10:00';

    bookingModal.show();
}

// ========== Funciones de Salas ==========
// ========== Renderizado de Salas ==========
function renderRooms(rooms) {
    const roomList = document.getElementById('room-list');
    if (!roomList) return;

    // Limpiar lista existente
    roomList.innerHTML = '';

    // Generar HTML para cada sala
    rooms.forEach(room => {
        const roomElement = document.createElement('div');
        roomElement.className = 'col-md-4 mb-4';
        roomElement.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${room.name}</h5>
                    <p class="card-text">${room.description || 'Sin descripción'}</p>
                    <p class="card-text"><small>Capacidad: ${room.capacity}</small></p>
                    <button class="btn btn-primary book-room-btn" 
                            data-room-id="${room.id}">
                        Reservar
                    </button>
                </div>
            </div>
        `;
        roomList.appendChild(roomElement);
    });

    // Agregar event listeners a los botones
    document.querySelectorAll('.book-room-btn').forEach(button => {
        button.addEventListener('click', () => {
            const roomId = button.getAttribute('data-room-id');
            openBookingModal(new Date().toISOString().split('T')[0], roomId);
        });
    });
}

// Función loadRooms corregida
async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}rooms/`, {
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const contentType = response.headers.get('content-type');
        if (!contentType?.includes('application/json')) {
            throw new TypeError("La respuesta no es JSON");
        }
        
        const data = await response.json();
        renderRooms(data.data);  // Ajusta según tu estructura de respuesta
    } catch (error) {
        console.error('Error cargando salas:', error);
        showNotification('Error al cargar salas', 'danger');
    }
}

// ========== Inicialización ==========
document.addEventListener("DOMContentLoaded", function() {
    // Inicializar modal
    const bookingModalEl = document.getElementById("bookingModal");
    if (bookingModalEl) {
        bookingModal = new bootstrap.Modal(bookingModalEl);
    }

    // Configurar formulario de reserva
    const bookingForm = document.getElementById("booking-form");
    if (bookingForm) {
        bookingForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const formData = {
                room: currentRoomId,
                title: document.getElementById('booking-title').value,
                start_time: document.getElementById('booking-start').value,
                end_time: document.getElementById('booking-end').value,
                email: document.getElementById('booking-email').value,
                phone: document.getElementById('booking-phone').value
            };

            fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) throw new Error('Error al crear reserva');
                return response.json();
            })
            .then(() => {
                bookingModal.hide();
                bookingForm.reset();
                showNotification('Reserva creada exitosamente', 'success');
                refreshCalendar();
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error al crear reserva', 'danger');
            });
        });
    }

    // Cargar datos iniciales
    loadRooms();
    initCalendar();

    // Configurar búsqueda
    const searchInput = document.getElementById("search-room");
    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll("#room-list .col-md-4").forEach(room => {
                const text = room.textContent.toLowerCase();
                room.style.display = text.includes(query) ? "" : "none";
            });
        });
    }
});