// API Endpoints
const API_BASE = '/api/items';
const API_HEALTH = '/api/health';

// DOM Elements
const itemsGrid = document.getElementById('itemsGrid');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const statusFilter = document.getElementById('statusFilter');

const countTotal = document.getElementById('countTotal');
const countPending = document.getElementById('countPending');
const countInProgress = document.getElementById('countInProgress');
const countCompleted = document.getElementById('countCompleted');

const healthIndicator = document.getElementById('healthIndicator');
const healthText = document.getElementById('healthText');

// Modal Elements
const itemModal = document.getElementById('itemModal');
const itemForm = document.getElementById('itemForm');
const modalTitle = document.getElementById('modalTitle');
const itemIdInput = document.getElementById('itemId');
const itemTitleInput = document.getElementById('itemTitle');
const itemCategoryInput = document.getElementById('itemCategory');
const itemStatusInput = document.getElementById('itemStatus');
const itemDescInput = document.getElementById('itemDescription');
const openCreateModalBtn = document.getElementById('openCreateModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelModalBtn = document.getElementById('cancelModalBtn');
const emptyAddBtn = document.getElementById('emptyAddBtn');
const toastContainer = document.getElementById('toastContainer');

// Local in-memory cache for fast search & filtering
let allItems = [];

// --- Toast Notifications ---
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Helper to escape HTML characters
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Format ISO date cleanly
function formatDate(isoStr) {
    if (!isoStr) return '';
    try {
        const d = new Date(isoStr);
        return d.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return isoStr;
    }
}

// --- Check API Health ---
async function checkHealth() {
    try {
        const res = await fetch(API_HEALTH);
        if (res.ok) {
            const data = await res.json();
            healthIndicator.classList.add('online');
            healthText.textContent = `Online (${data.total_items} items)`;
        } else {
            throw new Error();
        }
    } catch {
        healthIndicator.classList.remove('online');
        healthText.textContent = 'Offline';
    }
}

// --- Load and Render Items ---
async function fetchItems() {
    try {
        const params = new URLSearchParams();
        if (categoryFilter.value) params.append('category', categoryFilter.value);
        if (statusFilter.value) params.append('status', statusFilter.value);
        if (searchInput.value.trim()) params.append('search', searchInput.value.trim());

        const res = await fetch(`${API_BASE}?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch items');
        
        allItems = await res.json();
        renderItems(allItems);
        updateMetrics();
        checkHealth();
    } catch (err) {
        showToast('Error loading items from server', 'error');
        console.error(err);
    }
}

function updateMetrics() {
    // Calculate metrics directly
    const total = allItems.length;
    const pending = allItems.filter(i => i.status === 'Pending').length;
    const inProgress = allItems.filter(i => i.status === 'In Progress').length;
    const completed = allItems.filter(i => i.status === 'Completed').length;

    countTotal.textContent = total;
    countPending.textContent = pending;
    countInProgress.textContent = inProgress;
    countCompleted.textContent = completed;
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'In Progress': return 'status-in-progress';
        case 'Completed': return 'status-completed';
        default: return 'status-pending';
    }
}

function renderItems(items) {
    itemsGrid.innerHTML = '';

    if (!items || items.length === 0) {
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.setAttribute('data-id', item.id);

        const statusClass = getStatusBadgeClass(item.status);

        card.innerHTML = `
            <div>
                <div class="card-top">
                    <div class="badge-group">
                        <span class="status-badge ${statusClass}">
                            ● ${escapeHtml(item.status)}
                        </span>
                        <span class="category-tag">${escapeHtml(item.category || 'General')}</span>
                    </div>
                    <span class="item-id text-muted" style="font-size:0.75rem; font-weight:600;">#${item.id}</span>
                </div>
                <div class="card-content" style="margin-top: 12px;">
                    <h3 class="card-title">${escapeHtml(item.title)}</h3>
                    <p class="card-desc">${escapeHtml(item.description || 'No description provided.')}</p>
                </div>
            </div>
            
            <div class="card-footer">
                <span>Updated ${formatDate(item.updated_at)}</span>
                <div class="card-actions">
                    <button class="btn-icon" title="Cycle Status" onclick="cycleStatus(${item.id})">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                    </button>
                    <button class="btn-icon" title="Edit Item" onclick="openEditModal(${item.id})">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                    </button>
                    <button class="btn-icon delete" title="Delete Item" onclick="deleteItem(${item.id})">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </div>
        `;

        itemsGrid.appendChild(card);
    });
}

// --- Quick Status Cycle ---
window.cycleStatus = async function(id) {
    const item = allItems.find(i => i.id === id);
    if (!item) return;

    const sequence = ['Pending', 'In Progress', 'Completed'];
    const currentIndex = sequence.indexOf(item.status);
    const nextStatus = sequence[(currentIndex + 1) % sequence.length];

    try {
        const res = await fetch(`${API_BASE}/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: nextStatus })
        });

        if (!res.ok) throw new Error('Status update failed');
        const updated = await res.json();
        showToast(`Item #${id} updated to "${nextStatus}"`, 'success');
        fetchItems();
    } catch (err) {
        showToast('Failed to update status', 'error');
        console.error(err);
    }
};

// --- Modal Handling ---
function openCreateModal() {
    modalTitle.textContent = 'Create New Item';
    itemIdInput.value = '';
    itemTitleInput.value = '';
    itemCategoryInput.value = 'General';
    itemStatusInput.value = 'Pending';
    itemDescInput.value = '';

    itemModal.classList.add('active');
    itemTitleInput.focus();
}

window.openEditModal = function(id) {
    const item = allItems.find(i => i.id === id);
    if (!item) return;

    modalTitle.textContent = `Edit Item #${id}`;
    itemIdInput.value = item.id;
    itemTitleInput.value = item.title;
    itemCategoryInput.value = item.category || 'General';
    itemStatusInput.value = item.status;
    itemDescInput.value = item.description || '';

    itemModal.classList.add('active');
    itemTitleInput.focus();
};

function closeModal() {
    itemModal.classList.remove('active');
}

// --- Form Submit (Create or Update) ---
itemForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = itemIdInput.value;
    const payload = {
        title: itemTitleInput.value.trim(),
        category: itemCategoryInput.value.trim() || 'General',
        status: itemStatusInput.value,
        description: itemDescInput.value.trim()
    };

    if (!payload.title) {
        showToast('Title is required', 'error');
        return;
    }

    try {
        const isEditing = Boolean(id);
        const url = isEditing ? `${API_BASE}/${id}` : API_BASE;
        const method = isEditing ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'Failed to save item');
        }

        const savedItem = await res.json();
        showToast(isEditing ? `Item #${id} updated!` : `Created item "${savedItem.title}"!`, 'success');
        closeModal();
        fetchItems();
    } catch (err) {
        showToast(err.message, 'error');
        console.error(err);
    }
});

// --- Delete Item ---
window.deleteItem = async function(id) {
    const item = allItems.find(i => i.id === id);
    const itemTitle = item ? item.title : `Item #${id}`;

    if (!confirm(`Are you sure you want to delete "${itemTitle}"?`)) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/${id}`, {
            method: 'DELETE'
        });

        if (!res.ok) throw new Error('Failed to delete item');
        showToast(`Item #${id} deleted`, 'info');
        fetchItems();
    } catch (err) {
        showToast('Error deleting item', 'error');
        console.error(err);
    }
};

// --- Event Listeners ---
openCreateModalBtn.addEventListener('click', openCreateModal);
emptyAddBtn.addEventListener('click', openCreateModal);
closeModalBtn.addEventListener('click', closeModal);
cancelModalBtn.addEventListener('click', closeModal);

// Close modal on background click
itemModal.addEventListener('click', (e) => {
    if (e.target === itemModal) closeModal();
});

// Filters and search
let searchDebounceTimer = null;
searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(fetchItems, 250);
});

categoryFilter.addEventListener('change', fetchItems);
statusFilter.addEventListener('change', fetchItems);

// Metric card filter shortcuts
document.querySelectorAll('.metric-card').forEach(card => {
    card.addEventListener('click', () => {
        const filter = card.getAttribute('data-filter');
        if (filter === 'all') {
            statusFilter.value = '';
        } else {
            statusFilter.value = filter;
        }
        fetchItems();
    });
});

// Initial boot
document.addEventListener('DOMContentLoaded', () => {
    fetchItems();
    checkHealth();
    // Periodic health ping
    setInterval(checkHealth, 30000);
});
