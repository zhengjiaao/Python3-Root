/**
 * Platform Admin - Common JavaScript
 */

// HTML escape to prevent XSS
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Escape string for use inside onclick attribute (single-quoted)
function escapeAttr(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}

// Toast notification system
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) {
        // 降级到 alert
        alert(message);
        return;
    }

    const iconMap = {
        success: 'bi-check-circle-fill',
        danger: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info: 'bi-info-circle-fill',
    };
    const bgMap = {
        success: 'bg-success',
        danger: 'bg-danger',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-dark',
    };

    const id = 'toast-' + Date.now();
    const html = `
        <div id="${id}" class="toast align-items-center ${bgMap[type] || 'bg-secondary'} text-white border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${iconMap[type] || 'bi-info-circle'} me-2"></i>${escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`;
    container.insertAdjacentHTML('beforeend', html);

    const toastEl = document.getElementById(id);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// Token 刷新锁，防止并发 401 时多次刷新
let _refreshPromise = null;

async function _doRefreshToken() {
    const refreshRes = await fetch('/api/auth/refresh', { method: 'POST' });
    if (!refreshRes.ok) return false;
    const refreshData = await refreshRes.json();
    return refreshData.code === 200;
}

// API helper
// Options: { noRedirect: true } to suppress auto-redirect on 401
async function apiFetch(url, options = {}) {
    const { noRedirect = false, ...fetchOptions } = options;
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
    };
    const config = { ...defaults, ...fetchOptions };
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    let response = await fetch(url, config);

    // 如果 Access Token 过期（401），尝试用 Refresh Token 刷新
    if (response.status === 401 && !noRedirect) {
        if (!_refreshPromise) {
            _refreshPromise = _doRefreshToken();
        }
        const success = await _refreshPromise;
        _refreshPromise = null;
        if (success) {
            response = await fetch(url, config);
        } else {
            window.location.href = '/login';
            return null;
        }
    }

    // Handle non-JSON responses (e.g. 500 HTML error pages)
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
        if (response.status === 401 && !noRedirect) {
            window.location.href = '/login';
        }
        return { code: response.status, message: `Server error: ${response.status}`, data: null };
    }

    const data = await response.json();

    // 处理业务层错误码
    if (data.code && data.code !== 200 && !noRedirect) {
        if (data.code === 401) {
            window.location.href = '/login';
            return null;
        }
        // 非401错误：让调用方自行处理，不再静默
    }

    return data;
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
}

// Confirm dialog
function confirmAction(message) {
    return window.confirm(message);
}

// Reusable pagination renderer
function renderPagination(containerId, total, page, pageSize) {
    const totalPages = Math.ceil(total / pageSize);
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 0) return;

    let html = '';
    const maxVisible = 5;
    let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    if (page > 1) {
        html += `<button class="btn btn-sm btn-outline-primary" onclick="loadPage(${page - 1})">&laquo;</button> `;
    }
    if (startPage > 1) {
        html += `<button class="btn btn-sm btn-outline-primary" onclick="loadPage(1)">1</button> `;
        if (startPage > 2) html += '<span class="btn btn-sm btn-outline-secondary disabled">...</span> ';
    }
    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="btn btn-sm ${i === page ? 'btn-primary' : 'btn-outline-primary'}" onclick="loadPage(${i})">${i}</button> `;
    }
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += '<span class="btn btn-sm btn-outline-secondary disabled">...</span> ';
        html += `<button class="btn btn-sm btn-outline-primary" onclick="loadPage(${totalPages})">${totalPages}</button> `;
    }
    if (page < totalPages) {
        html += `<button class="btn btn-sm btn-outline-primary" onclick="loadPage(${page + 1})">&raquo;</button>`;
    }
    container.innerHTML = html;
}