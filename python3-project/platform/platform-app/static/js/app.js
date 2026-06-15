// ============================================================
// Platform App - Common Scripts
// ============================================================

function showToast(message, type) {
    const toastEl = document.getElementById('globalToast');
    const toastBody = document.getElementById('toastMessage');
    if (!toastEl || !toastBody) return;

    toastBody.textContent = message;
    toastEl.className = 'toast align-items-center text-white border-0 bg-' + type;
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
}

// Token 刷新锁，防止并发 401 时多次刷新
let _refreshPromise = null;

async function _doRefreshToken() {
    const refreshRes = await fetch('/api/auth/refresh', { method: 'POST' });
    if (!refreshRes.ok) return false;
    const refreshData = await refreshRes.json();
    return refreshData.code === 200;
}

// API helper（支持 Access Token 自动刷新）
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

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
        if (response.status === 401 && !noRedirect) {
            window.location.href = '/login';
        }
        return { code: response.status, message: 'Server error: ' + response.status, data: null };
    }

    const data = await response.json();

    // 处理业务层错误码
    if (data.code && data.code !== 200 && !noRedirect) {
        if (data.code === 401) {
            window.location.href = '/login';
            return null;
        }
    }

    return data;
}

async function handleLogout(e) {
    if (e) e.preventDefault();
    try {
        const json = await apiFetch('/api/auth/logout', { method: 'POST' });
        if (json && json.code === 200) {
            showToast('已退出登录', 'success');
            setTimeout(() => { window.location.href = '/'; }, 500);
        } else {
            showToast(json ? (json.message || '退出失败') : '退出失败', 'danger');
        }
    } catch (err) {
        showToast('网络错误', 'danger');
    }
}

// 页面加载完成后初始化导航栏登录状态
async function initNavUser() {
    try {
        const json = await apiFetch('/api/home/info', { noRedirect: true });
        if (json && json.code === 200 && json.data && json.data.user) {
            const user = json.data.user;
            const navLogin = document.getElementById('navLogin');
            const navProfile = document.getElementById('navProfile');
            const navLogout = document.getElementById('navLogout');
            const navNickname = document.getElementById('navNickname');
            if (navLogin) navLogin.classList.add('d-none');
            if (navProfile) navProfile.classList.remove('d-none');
            if (navLogout) navLogout.classList.remove('d-none');
            if (navNickname) navNickname.textContent = user.nickname || user.username;
        }
    } catch (err) {
        // 静默处理，未登录时不显示错误
    }
}

document.addEventListener('DOMContentLoaded', initNavUser);
