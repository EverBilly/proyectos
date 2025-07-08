// ========== Obtiene el token CSRF ==========
function getCookie(name) {
    let cookieValue = null;
    if(document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if(cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
console.log("CSRF Token obtenido: ", csrftoken);

document.addEventListener("DOMContentLoaded", function () {
    const roomList = document.getElementById("room-list");
    const roomForm = document.getElementById("room-form");
  
    const bookingModalEl = document.getElementById("bookingModal");
    const bookingModal = new bootstrap.Modal(bookingModalEl);
  
    let currentRoomId = null;
  
    // ========== Cargar salas ==========
    function loadRooms() {
      fetch("/api/rooms/")
        .then(res => res.json())
        .then(data => {
          roomList.innerHTML = "";
          data.forEach(room => {
            const col = document.createElement("div");
            col.className = "col-md-4";
  
            col.innerHTML = `
              <div class="card h-100 shadow-sm">
                <div class="card-body d-flex flex-column">
                  <h5 class="card-title">${room.name}</h5>
                  <p class="card-text text-muted">${room.description || "Sin descripción"}</p>
                  <p class="${room.status === 'disponible' ? 'text-success' : 'text-danger'}">
                    Estado: ${room.status}
                  </p>
                  <button class="btn btn-primary mt-auto mb-2" onclick="openBookingModal(${room.id})">Reservar</button>
                  <button class="btn btn-warning btn-sm" onclick="editRoom(${room.id})">Editar</button>
                  <button class="btn btn-danger btn-sm mt-1" onclick="deleteRoom(${room.id})">Eliminar</button>
                </div>
              </div>
            `;
  
            roomList.appendChild(col);
          });
        })
        .catch(err => console.error("Error cargando salas:", err));
    }
  
    window.openBookingModal = function (roomId) {
      currentRoomId = roomId;
      document.getElementById("booking-room-id").value = roomId;
      bookingModal.show();
    };
  
    // ========== Crear sala ==========
    roomForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const name = document.getElementById("room-name").value.trim();
      const description = document.getElementById("room-description").value.trim();
  
      fetch("/api/rooms/", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken 
        },
        credentials: 'same-origin',
        body: JSON.stringify({ name, description, status: "disponible" }),
      })
      .then(res => {
        console.log("Respuesta al crear sala: ", res.status);
        return res.json();
      })
      .then(() => {
        document.getElementById("room-form").reset();
        loadRooms();
      })
      .catch(err => console.error("Error al crear sala:", err));
    });
  
    // ========== Cargar y renderizar calendario ==========
    function loadBookings() {
      fetch("/api/bookings/")
        .then(res => res.json())
        .then(events => {
          console.log("Datos de eventos:", events); // 👈 Para ver qué devuelve la API
          renderCalendar(events);
        })
        .catch(err => console.error("Error al cargar citas:", err));
    }
  
    function renderCalendar(events = []) {
      const calendarEl = document.getElementById("calendar");
  
      if (!calendarEl) {
        console.warn("No se encontró el elemento #calendar");
        return;
      }
  
      // Si hay un calendario previo, destrúyelo
      if (window.calendar) {
        try {
          window.calendar.destroy();
        } catch (err) {
          console.warn("No se pudo destruir el calendario:", err);
        }
      }
  
      // Solo usa eventos con datos válidos
      const validEvents = events.filter(e => e.start_time && e.end_time && Date.parse(e.start_time) && Date.parse(e.end_time))
                               .map(e => ({
                                 id: e.id,
                                 title: e.title || "Sin título",
                                 start: e.start_time,
                                 end: e.end_time
                               }));
  
      // Crea el nuevo calendario
      window.calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: 'es',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        editable: true,
        droppable: true,
        selectable: true,
        selectMirror: true,
        events: validEvents,
        eventClick: function(info) {
          if (confirm(`¿Eliminar evento "${info.event.title}"?`)) {
            fetch(`/api/bookings/${info.event.id}/`, {
              method: "DELETE",
              headers: {
                "X-CSRFToken": csrftoken
              },
              credentials: 'same-origin'
            }).then(() => loadBookings());
          }
        }
      });
  
      window.calendar.render();
    }
  
    // ========== Crear cita ==========
    document.getElementById("booking-form").addEventListener("submit", function (e) {
      e.preventDefault();
      const title = document.getElementById("booking-title").value.trim();
      const start = document.getElementById("booking-start").value;
      const end = document.getElementById("booking-end").value;
      const email = document.getElementById("booking-email").value.trim();
      const phone = document.getElementById("booking-phone").value.trim();
  
      fetch("/api/bookings/", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
         },
        credentials: 'same-origin',
        body: JSON.stringify({
          room: currentRoomId,
          title,
          start_time: start,
          end_time: end,
          email,
          phone
        }),
      })
      .then(res => {
        console.log("Respuesta al crear cita: ", res.status);
        return res.json();
      })
      .then(() => {
        document.getElementById("booking-form").reset();
        bookingModal.hide();
        loadBookings();
      })
      .catch(err => console.error("Error al crear cita:", err));
    });
  
    // ========== Editar sala ==========
    window.editRoom = function(id) {
      const newName = prompt("Nuevo nombre de la sala:");
      if (!newName) return;
  
      fetch(`/api/rooms/${id}/`, {
        method: "PUT",
        headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken 
        },
        credentials: 'same-origin',
        body: JSON.stringify({ name: newName })
      })
      .then(() => loadRooms())
      .catch(err => console.error("Error al editar sala:", err));
    };
  
    // ========== Eliminar sala ==========
    window.deleteRoom = function(id) {
      if (!confirm("¿Estás seguro de eliminar esta sala?")) return;
  
      fetch(`/api/rooms/${id}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken
        },
        credentials: 'same-origin'
      })
      .then(() => loadRooms())
      .catch(err => console.error("Error al eliminar sala:", err));
    };
  
    // ========== Iniciar aplicación ==========
    loadRooms();
    loadBookings();
  });