// Global Toast Notification Helper
function showToast(message, type = 'success') {
    // Check if container exists, else create it
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '24px';
        container.style.right = '24px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.padding = '16px 24px';
    toast.style.borderRadius = '8px';
    toast.style.color = '#ffffff';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '600';
    toast.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.4)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '12px';
    toast.style.transform = 'translateY(-20px)';
    toast.style.opacity = '0';
    toast.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

    // Icon & Color styling based on type
    let color = '#10b981'; // success
    let icon = `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>`;
    
    if (type === 'error' || type === 'danger') {
        color = '#ef4444';
        icon = `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;
    } else if (type === 'warning') {
        color = '#f59e0b';
        icon = `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;
    } else if (type === 'info') {
        color = '#8b5cf6';
        icon = `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    }

    toast.style.backgroundColor = color;
    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    // Trigger Entrance animation
    setTimeout(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    }, 10);

    // Exit animation and cleanup
    setTimeout(() => {
        toast.style.transform = 'translateY(-20px)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// Global modal toggle helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Formatting helpers
function formatMoney(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    // Handle formats like "Fri, 10 May 2026 00:00:00 GMT" or ISO
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('pt-BR');
}
