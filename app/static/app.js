let isDemoMode = true;
let token = null;

// Fake Data for Demo Mode
let demoItems = [
    { id: "item-123", url: "https://store.apple.com/iphone15", size: "Pro Max 256GB", interval: 300 },
    { id: "item-456", url: "https://amazon.com/rtx-4090", size: "", interval: 600 }
];
let demoProcessRunning = true;

document.addEventListener("DOMContentLoaded", () => {
    checkAuth();
    refreshData();
});

function checkAuth() {
    token = localStorage.getItem("access_token");
    const badge = document.getElementById("mode-badge");
    const authBtn = document.getElementById("auth-btn");

    if (token) {
        isDemoMode = false;
        badge.textContent = "Live Mode";
        badge.className = "badge badge-live";
        authBtn.textContent = "Logout";
        authBtn.onclick = handleLogout;
    } else {
        isDemoMode = true;
        badge.textContent = "Demo Mode";
        badge.className = "badge badge-demo";
        authBtn.textContent = "Login";
        authBtn.onclick = openLoginModal;
    }
}

// UI Helpers
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function openLoginModal() {
    document.getElementById("login-overlay").classList.add("active");
}
function closeLoginModal() {
    document.getElementById("login-overlay").classList.remove("active");
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
}

function openEditModal(id, url, intervalSeconds) {
    document.getElementById("edit-item-id").value = id;
    document.getElementById("edit-item-url").value = url;
    
    let value = intervalSeconds / 60;
    let unit = "minutes";
    if (value >= 60 && value % 60 === 0) {
        value = value / 60;
        unit = "hours";
    }
    
    document.getElementById("edit-item-interval-value").value = value;
    document.getElementById("edit-item-interval-unit").value = unit;
    
    document.getElementById("edit-overlay").classList.add("active");
}

function closeEditModal() {
    document.getElementById("edit-overlay").classList.remove("active");
}

// Authentication
async function handleLogin() {
    const usernameInput = document.getElementById("login-username").value;
    const passwordInput = document.getElementById("login-password").value;

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            showToast("Successfully logged in", "success");
            closeLoginModal();
            checkAuth();
            refreshData();
        } else {
            showToast("Invalid credentials", "error");
        }
    } catch (e) {
        showToast("Login error", "error");
    }
}

function handleLogout() {
    localStorage.removeItem("access_token");
    checkAuth();
    refreshData();
    showToast("Logged out", "success");
}

// Data Fetching and Rendering
async function refreshData() {
    await fetchSettings();
    await fetchProcessStatus();
    await fetchItems();
}

async function fetchSettings() {
    if (isDemoMode) {
        document.getElementById("target-email").value = "demo@example.com";
        document.getElementById("logging-toggle").checked = true;
        return;
    }

    try {
        const res = await fetch("/settings/", { headers: getHeaders() });
        if (res.ok) {
            const data = await res.json();
            document.getElementById("target-email").value = data.email_to || "";
            document.getElementById("logging-toggle").checked = data.logging_enabled;
        }
    } catch (e) {
        console.error("Error fetching settings");
    }
}

function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function fetchProcessStatus() {
    const statusText = document.getElementById("process-status-text");
    const indicator = document.getElementById("process-status-badge");

    if (isDemoMode) {
        statusText.textContent = demoProcessRunning ? "Process is running (Demo)." : "Process is stopped (Demo).";
        indicator.className = demoProcessRunning ? "status-indicator up" : "status-indicator down";
        return;
    }

    try {
        const res = await fetch("/process/status", { headers: getHeaders() });
        if (res.ok) {
            const data = await res.json();
            statusText.textContent = data.message;
            indicator.className = data.is_running ? "status-indicator up" : "status-indicator down";
        }
    } catch (e) {
        statusText.textContent = "Error fetching status";
        indicator.className = "status-indicator down";
    }
}

async function fetchItems() {
    const tbody = document.querySelector("#items-table tbody");
    tbody.innerHTML = "";

    let items = [];
    if (isDemoMode) {
        items = demoItems;
    } else {
        try {
            const res = await fetch("/item/list", { headers: getHeaders() });
            if (res.ok) {
                const data = await res.json();
                // data.items is a dictionary mapping id -> {url, sizes, interval_seconds}
                for (const [id, itemData] of Object.entries(data.items)) {
                    if (itemData.sizes && itemData.sizes.length > 0) {
                        itemData.sizes.forEach(s => {
                            items.push({
                                id: id,
                                url: itemData.url,
                                size: s,
                                interval: itemData.interval_seconds
                            });
                        });
                    } else {
                        items.push({
                            id: id,
                            url: itemData.url,
                            size: "",
                            interval: itemData.interval_seconds
                        });
                    }
                }
            }
        } catch (e) {
            console.error("Error fetching items");
        }
    }

    if (items.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5'>No items found.</td></tr>";
        return;
    }

    items.forEach(item => {
        const tr = document.createElement("tr");
        const minutes = Math.round(item.interval / 60);
        const intervalText = (minutes >= 60 && minutes % 60 === 0) ? `${minutes / 60} h` : `${minutes} min`;
        tr.innerHTML = `
            <td><a href="${item.url}" target="_blank" style="color: var(--accent-primary); text-decoration: none;">${item.url.substring(0, 40)}...</a></td>
            <td>${item.size || "-"}</td>
            <td>${intervalText}</td>
            <td style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: var(--warning-color); border: none; color: white;" onclick="openEditModal('${item.id}', '${item.url}', ${item.interval})">Edit</button>
                <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="deleteItem('${item.id}', '${item.size}')">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Actions
async function actionProcess(action) {
    if (isDemoMode) {
        showToast(`Demo Mode: Process ${action} simulated`, "demo");
        if (action === 'start' || action === 'restart') demoProcessRunning = true;
        if (action === 'stop') demoProcessRunning = false;
        fetchProcessStatus();
        return;
    }

    try {
        const res = await fetch(`/process/${action}`, { method: "POST", headers: getHeaders() });
        const data = await res.json();
        if (res.ok) {
            showToast(data.message, "success");
        } else {
            const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
            showToast(errorMsg || "Error performing action", "error");
        }
        fetchProcessStatus();
    } catch (e) {
        showToast(`Network error while performing ${action}`, "error");
    }
}

async function handleAddItem(e) {
    e.preventDefault();
    const url = document.getElementById("item-url").value;
    const size = document.getElementById("item-size").value;
    const interval_value = parseInt(document.getElementById("item-interval-value").value);
    const interval_unit = document.getElementById("item-interval-unit").value;

    if (isDemoMode) {
        showToast("Demo Mode: Item added (simulated)", "demo");
        demoItems.push({
            id: `demo-item-${Date.now()}`,
            url, size, interval: interval_value * (interval_unit === 'minutes' ? 60 : (interval_unit === 'hours' ? 3600 : 1))
        });
        fetchItems();
        e.target.reset();
        return;
    }

    try {
        const res = await fetch("/item/add", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ url, size, interval_value, interval_unit })
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast("Item added successfully", "success");
            e.target.reset();
            fetchItems();
        } else {
            const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
            showToast(errorMsg || "Error adding item", "error");
        }
    } catch (err) {
        showToast("Network error or server unavailable", "error");
    }
}

async function deleteItem(id, size) {
    if (isDemoMode) {
        showToast("Demo Mode: Item deleted (simulated)", "demo");
        demoItems = demoItems.filter(i => i.id !== id);
        fetchItems();
        return;
    }

    if (!confirm("Are you sure you want to delete this item?")) return;

    try {
        const res = await fetch("/item/delete", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ id, size })
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast("Item deleted", "success");
            fetchItems();
        } else {
            const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
            showToast(errorMsg || "Error deleting item", "error");
        }
    } catch (err) {
        showToast("Network error or server unavailable", "error");
    }
}

async function handleEditItem() {
    const id = document.getElementById("edit-item-id").value;
    const url = document.getElementById("edit-item-url").value;
    const interval_value = parseInt(document.getElementById("edit-item-interval-value").value);
    const interval_unit = document.getElementById("edit-item-interval-unit").value;

    if (isDemoMode) {
        showToast("Demo Mode: Item updated (simulated)", "demo");
        const idx = demoItems.findIndex(i => i.id === id);
        if (idx > -1) {
            demoItems[idx].url = url;
            demoItems[idx].interval = interval_value * (interval_unit === 'minutes' ? 60 : 3600);
        }
        closeEditModal();
        fetchItems();
        return;
    }

    try {
        const res = await fetch("/item/update", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ id, url, interval_value, interval_unit })
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast("Item updated successfully", "success");
            closeEditModal();
            fetchItems();
        } else {
            const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
            showToast(errorMsg || "Error updating item", "error");
        }
    } catch (err) {
        showToast("Network error or server unavailable", "error");
    }
}

async function toggleLogging() {
    const isEnabled = document.getElementById("logging-toggle").checked;
    
    if (isDemoMode) {
        showToast(`Demo Mode: Logging ${isEnabled ? 'enabled' : 'disabled'}`, "demo");
        return;
    }

    try {
        const res = await fetch("/settings/logging", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ enabled: isEnabled })
        });
        if (res.ok) {
            showToast(`Logging ${isEnabled ? 'enabled' : 'disabled'}`, "success");
        } else {
            showToast("Failed to change logging setting", "error");
            document.getElementById("logging-toggle").checked = !isEnabled;
        }
    } catch (e) {
        showToast("Error changing settings", "error");
        document.getElementById("logging-toggle").checked = !isEnabled;
    }
}

async function updateEmail() {
    const email = document.getElementById("target-email").value;
    
    if (isDemoMode) {
        showToast("Demo Mode: Email updated (simulated)", "demo");
        return;
    }

    try {
        const res = await fetch("/settings/email", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ email })
        });
        if (res.ok) {
            showToast("Target email updated", "success");
        } else {
            showToast("Failed to update email", "error");
        }
    } catch (e) {
        showToast("Error updating email", "error");
    }
}
