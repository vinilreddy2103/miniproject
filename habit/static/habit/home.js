document.addEventListener("DOMContentLoaded", fetchHabits);

function openModal(editing = false) {
    document.getElementById("habit-modal").style.display = "block";
    document.getElementById("modal-overlay").style.display = "block";

    if (!editing) {
        // Reset form fields for new habit
        document.getElementById("modal-title").innerText = "Add New Habit";
        document.getElementById("habit-name").value = "";
        document.getElementById("habit-type").value = "measurable";
        document.getElementById("habit-target").value = "1";
        document.getElementById("habit-modal").removeAttribute("data-habit-id");
    }

    toggleTargetCount();
}

function closeModal() {
    document.getElementById("habit-modal").style.display = "none";
    document.getElementById("modal-overlay").style.display = "none";
    document.getElementById("habit-modal").removeAttribute("data-habit-id"); // Reset habit ID
}

function toggleTargetCount() {
    const habitType = document.getElementById("habit-type").value;
    document.getElementById("habit-target-wrapper").style.display = habitType === "measurable" ? "block" : "none";
}

function fetchHabits() {
    fetch("/habit/api/user-habits/")
        .then(response => response.json())
        .then(data => {
            const incompleteHabits = document.getElementById("incomplete-habits");
            const completedHabits = document.getElementById("completed-habits");

            incompleteHabits.innerHTML = "";
            completedHabits.innerHTML = "";

            data.habits.forEach(habit => {
                const habitDiv = createHabitElement(habit);
                if (habit.completed) {
                    completedHabits.appendChild(habitDiv);
                } else {
                    incompleteHabits.appendChild(habitDiv);
                }
            });
        })
        .catch(error => console.error("Error fetching habits:", error));
}

function createHabitElement(habit) {
    const habitDiv = document.createElement("div");
    habitDiv.classList.add("habit");

    habitDiv.innerHTML = `
        ${habit.habit_type === "non-measurable" ? `<input type="checkbox" ${habit.completed ? "checked" : ""} onchange="completeHabit(${habit.id})">` : ""}
        <strong>${habit.name}</strong>
        ${habit.habit_type === "measurable" ? `
            <span id="progress-${habit.id}">Progress: ${habit.current_count}/${habit.target_count}</span>
            <button class="increment-btn" onclick="incrementHabit(${habit.id})">+</button>
        ` : ""}
        <span class="habit-streak" id="streak-${habit.id}">${habit.streak || 0}</span>
        <button class="edit-btn" onclick="editHabit(${habit.id}, '${habit.name}', '${habit.habit_type}', ${habit.target_count})">✏️</button>
        <button class="delete-btn" onclick="deleteHabit(${habit.id})">🗑️</button>
        <button class="details-btn" onclick="openHabitDetail(${habit.id})">📅</button>
    `;
    //habitDiv.addEventListener("click", () => openHabitDetail(habit.id));

    return habitDiv;
}


function incrementHabit(habitId) {
    fetch(`/habit/api/update-habit/${habitId}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
        body: JSON.stringify({ current_count: "increment" })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById(`progress-${habitId}`).innerText = `Progress: ${data.new_progress}/${data.target}`;

                // If progress reaches the target, mark habit as completed
                if (data.new_progress >= data.target) {
                    completeHabit(habitId);
                } else {
                    fetchHabits();
                }
            }
        })
        .catch(error => console.error("Error incrementing habit:", error));
}


function completeHabit(habitId) {
    fetch(`/habit/api/complete-habit/${habitId}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
        body: JSON.stringify({ completed: true })
    })
        .then(() => {
            fetchHabits()
        })
        .catch(error => console.error("Error completing habit:", error));
}

function editHabit(id, name, type, target) {
    document.getElementById("modal-title").innerText = "Edit Habit";
    document.getElementById("habit-name").value = name;
    document.getElementById("habit-type").value = type;
    document.getElementById("habit-target").value = target;
    document.getElementById("habit-modal").setAttribute("data-habit-id", id);

    toggleTargetCount();
    openModal(true);
}

function saveHabit() {
    const name = document.getElementById("habit-name").value;
    const type = document.getElementById("habit-type").value;
    const target = document.getElementById("habit-target").value || 1;
    const habitId = document.getElementById("habit-modal").getAttribute("data-habit-id");

    if (!name) {
        alert("Enter a habit name!");
        return;
    }

    const habitData = { name, habit_type: type, target_count: parseInt(target) };
    const url = habitId ? `/habit/api/update-habit/${habitId}/` : "/habit/api/add-habit/";
    const method = habitId ? "PUT" : "POST";

    fetch(url, {
        method,
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
        body: JSON.stringify(habitData)
    })
        .then(() => { fetchHabits(); closeModal(); })
        .catch(error => console.error("Error saving habit:", error));
}

function deleteHabit(habitId) {
    if (!confirm("Are you sure you want to delete this habit?")) return;

    fetch(`/habit/api/delete-habit/${habitId}/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCSRFToken() }
    })
        .then(() => fetchHabits())
        .catch(error => console.error("Error deleting habit:", error));
}

function logout() {
    window.location.href = "/auth/logout/";
}


function getCSRFToken() {
    return document.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";
}

function openHabitDetail(habitId) {
    fetch(`/habit/api/habit-detail/${habitId}/`)
        .then(response => response.json())
        .then(data => {
            // Set habit details
            document.getElementById("habit-detail-name").innerText = `${data.name}`;
            document.getElementById("habit-detail-type").innerText = `${data.habit_type}`;
            document.getElementById("habit-detail-streak").innerText = `${data.streak || 0}`;

            if (data.habit_type === "measurable") {
                document.getElementById("habit-detail-progress").innerText =
                    `${data.current_count}/${data.target_count}`;
                document.getElementById("habit-detail-progress").style.display = "block";
            } else {
                document.getElementById("habit-detail-progress").style.display = "none";
            }

            // Display completed dates if available
            document.getElementById("habit-completed-dates").innerText =
                data.completed_dates?.length > 0
                    ? `${data.completed_dates.join(", ")}`
                    : "No completed dates available.";

            // Show and position the modal
            const modal = document.getElementById("habit-detail-modal");
            const overlay = document.getElementById("habit-detail-overlay");
            modal.style.display = "block";
            overlay.style.display = "block";

            modal.style.top = "10%";
            modal.style.left = "50%";
            modal.style.transform = "translate(-50%, 0)";
        })
        .catch(error => console.error("Error fetching habit detail:", error));
}

function closeHabitDetail() {
    document.getElementById("habit-detail-modal").style.display = "none";
    document.getElementById("habit-detail-overlay").style.display = "none";

    // Clear previous details to avoid stale data
    document.getElementById("habit-detail-name").innerText = "";
    document.getElementById("habit-detail-type").innerText = "";
    document.getElementById("habit-detail-streak").innerText = "";
    document.getElementById("habit-detail-progress").innerText = "";
    document.getElementById("habit-completed-dates").innerText = "";
}


