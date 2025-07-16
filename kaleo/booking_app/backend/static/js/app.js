// ========== Obtiene el token CSRF ==========
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

const csrftoken = getCookie('csrftoken');

// ========== Mostrar notificaciones ==========
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

// ========== Cargar salas ==========
function loadRooms() {
    fetch("/api/rooms/", {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(res => {
        if (res.status === 403 || res.status === 401) {
            window.location.href = "/login/";
            throw new Error("Acceso denegado – redirigido a login");
        }
        if (!res.ok) throw new Error(`Fallo HTTP ${res.status}`);
        return res.json();
    })
    .then(data => {
        const roomList = document.getElementById("room-list");
        if (!roomList) return;

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
    .catch(err => {
        console.error("Error cargando salas:", err.message);
        if (err.message.includes("403") || err.message.includes("401")) {
            showNotification("⚠️ Acceso denegado – inicia sesión", "danger");
            setTimeout(() => window.location.href = "/login/", 2000);
        } else {
            showNotification("❌ No se pudieron cargar las salas", "danger");
        }
    });
}

// ========== Cargar y renderizar calendario ==========
function loadBookings() {
    fetch("/api/bookings/", {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(res => {
        if (res.status === 403 || res.status === 401) {
            window.location.href = "/login/";
            throw new Error("No autorizado – redirigido");
        }
        if (!res.ok) throw new Error(`Fallo al cargar citas – status ${res.status}`);
        return res.json();
    })
    .then(events => {
        renderCalendar(events);
    })
    .catch(err => {
        console.error("Error al cargar citas:", err.message);
        if (err.message.includes("403") || err.message.includes("401")) {
            showNotification("🔒 Inicia sesión para ver el calendario", "danger");
            setTimeout(() => window.location.href = "/login/", 2000);
        } else {
            showNotification("❌ No se pudieron cargar las citas", "danger");
        }
    });
}

function renderCalendar(events = []) {
    const calendarEl = document.getElementById("calendar");

    if (!calendarEl) {
        console.warn("No se encontró el elemento #calendar");
        return;
    }

    // Destruir calendario anterior si existe
    if (window.calendar) {
        try {
            window.calendar.destroy();
        } catch (err) {
            console.warn("No se pudo destruir el calendario:", err);
        }
    }

    // Validar y filtrar eventos
    const validEvents = events
        .filter(e => e.start_time && e.end_time && Date.parse(e.start_time) && Date.parse(e.end_time))
        .map(e => ({
            id: e.id,
            title: e.title || "Sin título",
            start: e.start_time,
            end: e.end_time
        }));

    // Crear nuevo calendario
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
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/json"
                    },
                    credentials: 'same-origin'
                }).then(() => loadBookings());
            }
        }
    });

    window.calendar.render();
}

// ========== Formulario crear sala ==========
const roomForm = document.getElementById("room-form");
if (roomForm) {
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
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(() => {
            document.getElementById("room-name").value = "";
            document.getElementById("room-description").value = "";
            loadRooms();
            showNotification("✅ Sala creada exitosamente", "success");
        })
        .catch(err => {
            console.error("Error al crear sala:", err.message);
            showNotification("❌ Error al crear sala", "danger");
        });
    });
}

// ========== Modal para crear cita ==========
const bookingModalEl = document.getElementById("bookingModal");
if (bookingModalEl) {
    const bookingModal = new bootstrap.Modal(bookingModalEl);

    window.openBookingModal = function (roomId) {
        const roomInput = document.getElementById("booking-room-id");
        if (!roomInput) {
            console.error("No se encontró el campo #booking-room-id");
            showNotification("❌ Error al abrir formulario – recarga la página", "danger");
            return;
        }

        currentRoomId = roomId;
        roomInput.value = roomId;
        bookingModal.show();
    };
}

let currentRoomId = null;

function isValidTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    
    // Permite solo entre 7:00 AM y 9:00 PM
    return hours >= 7 && hours <= 21;
}

// ========== Crear cita ==========
const bookingForm = document.getElementById("booking-form");
if (bookingForm) {
    bookingForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const title = document.getElementById("booking-title").value.trim();
        const start = document.getElementById("booking-start").value;
        const end = document.getElementById("booking-end").value;
        const email = document.getElementById("booking-email").value.trim();
        const phone = document.getElementById("booking-phone").value.trim();

        if (!title || !start || !end) {
            showNotification("⚠️ Completa todos los campos", "danger");
            return;
        }

        const now = new Date();
        const startDate = new Date(start);
        const endDate = new Date(end);

        if (startDate < now) {
            showNotification("❌ No puedes reservar en el pasado", "danger");
            return;
        }

        if (endDate <= startDate) {
            showNotification("❌ La fecha de fin debe ser posterior a inicio", "danger");
            return;
        }

        if (!isValidTime(start) || !isValidTime(end)) {
            showNotification("⏰ Las citas deben estar entre 7:00 AM y 9:00 PM", "danger");
            return;
        }

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
            if (!res.ok) throw new Error(`Fallo al crear cita – status ${res.status}`);
            return res.json();
        })
        .then(() => {
            document.getElementById("booking-form").reset();
            bookingModal.hide();
            loadBookings();
            showNotification("✅ Cita creada exitosamente", "success");
        })
        .catch(err => {
            console.error("Error al crear cita:", err.message);
            showNotification("❌ Error al crear cita", "danger");
        });
    });
}

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
    .then(res => {
        if (!res.ok) throw new Error(`Fallo al editar sala – status ${res.status}`);
        return res.json();
    })
    .then(() => {
        loadRooms();
        showNotification("✏️ Sala actualizada", "info");
    })
    .catch(err => {
        console.error("Error al editar sala:", err.message);
        showNotification("❌ Error al actualizar sala", "danger");
    });
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
    .then(() => {
        loadRooms();
        showNotification("🗑️ Sala eliminada", "warning");
    })
    .catch(err => {
        console.error("Error al eliminar sala:", err);
        showNotification("❌ Error al eliminar sala", "danger");
    });
};

// ========== Búsqueda de salas ==========
const searchInput = document.getElementById("search-room");
if (searchInput) {
    searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase();
        const cols = document.querySelectorAll(".col-md-4");

        cols.forEach(col => {
            const nameEl = col.querySelector(".card-title");
            const descEl = col.querySelector(".card-text");

            const name = nameEl?.textContent.toLowerCase() || "";
            const description = descEl?.textContent.toLowerCase() || "";

            col.style.display = name.includes(query) || description.includes(query) ? "" : "none";
        });
    });
}

// ========== Iniciar aplicación ==========
// document.addEventListener("DOMContentLoaded", function () {
//     const roomList = document.getElementById("room-list");

//     if (roomList) loadRooms();
//     if (document.getElementById("calendar")) loadBookings();
// });



document.addEventListener("DOMContentLoaded", function () {
    const roomList = document.getElementById("room-list");
    const calendarEl = document.getElementById("calendar");
    const bookingModalEl = document.getElementById("bookingModal");

    if (typeof bootstrap === "undefined") {
        console.error("Bootstrap no está definido – revisa la carga de scripts");
        return;
    }

    if (bookingModalEl) {
        window.bookingModal = new bootstrap.Modal(bookingModalEl);
    } else {
        console.warn("No se encontró #bookingModal");
    }
    window.bookingModal = new bootstrap.Modal(bookingModalEl);

    fetch("/api/rooms/", {
        credentials: 'same-origin'
    })
    .then(res => {
        if (res.status === 401 || res.status === 403) {
            window.location.href = "/login/";
            throw new Error("Acceso denegado – redirigido");
        }
        return res.json();
    })
    .then(data => {
        if (roomList && data.length > 0) loadRooms(data);
    });

    if (calendarEl) {
        loadBookings();  // ← Solo carga el calendario si existe
    }
});