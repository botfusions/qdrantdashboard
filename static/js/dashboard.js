// Qdrant Dashboard - Main JavaScript
// Authentication, Theme Management, API Integration

console.log('🚀 Dashboard.js loaded! Version: 20251001-2 (with debug logs)');

// Configuration
const CONFIG = {
    QDRANT_URL: 'https://qdrant.turklawai.com',
    DEFAULT_PASSWORD: 'password', // Default password (plain text for demo)
    STORAGE_KEYS: {
        AUTH: 'qdrant_auth',
        THEME: 'qdrant_theme',
        PASSWORD: 'qdrant_password'
    },
    AUTO_REFRESH: 30000 // 30 seconds
};

// State Management
let state = {
    isAuthenticated: false,
    currentTheme: 'light',
    autoRefreshInterval: null,
    qdrantStatus: 'connecting'
};

// ============================================
// Authentication Functions
// ============================================

function checkAuth() {
    const stored = localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH);
    return stored === 'true';
}

async function login(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('auth_token', data.access_token);
            state.isAuthenticated = true;
            document.getElementById('login-overlay').classList.add('hidden');
            document.getElementById('login-error').textContent = '';
            initDashboard();
            addLog('Giris basarili');
            return true;
        } else {
            const error = await response.json();
            document.getElementById('login-error').textContent = error.detail || 'Hatali sifre!';
            return false;
        }
    } catch (error) {
        document.getElementById('login-error').textContent = 'Giris hatasi: ' + error.message;
        return false;
    }
}

async function logout() {
    try {
        const token = localStorage.getItem('auth_token');
        if (token) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('auth_token');
        state.isAuthenticated = false;
        location.reload();
    }
}

async function changePassword(oldPassword, newPassword) {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            alert('Sifre basariyla degistirildi!');
            addLog('Sifre degistirildi');
            return true;
        } else {
            const error = await response.json();
            alert('Hata: ' + (error.detail || 'Eski sifre hatali!'));
            return false;
        }
    } catch (error) {
        alert('Sifre degistirme hatasi: ' + error.message);
        return false;
    }
}

// ============================================
// Theme Management
// ============================================

function loadTheme() {
    const savedTheme = localStorage.getItem(CONFIG.STORAGE_KEYS.THEME) || 'light';
    state.currentTheme = savedTheme;
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    document.body.className = theme === 'dark' ? 'dark-theme' : 'light-theme';
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');

    if (theme === 'dark') {
        icon.textContent = '☀️';
        text.textContent = 'Gündüz Modu';
    } else {
        icon.textContent = '🌙';
        text.textContent = 'Gece Modu';
    }
}

function toggleTheme() {
    const newTheme = state.currentTheme === 'light' ? 'dark' : 'light';
    state.currentTheme = newTheme;
    localStorage.setItem(CONFIG.STORAGE_KEYS.THEME, newTheme);
    applyTheme(newTheme);
    addLog(`🎨 Tema değiştirildi: ${newTheme === 'dark' ? 'Gece' : 'Gündüz'} Modu`);
}

// ============================================
// API Integration
// ============================================

async function fetchQdrantStatus() {
    try {
        const response = await fetch('/api/qdrant/status');
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'online') {
                state.qdrantStatus = 'online';
                updateStatusBadge('online', 'Cevrimici');
                document.getElementById('qdrant-version').textContent = result.data?.version || 'v1.x';
                return true;
            }
        }
    } catch (error) {
        state.qdrantStatus = 'offline';
        updateStatusBadge('offline', 'Cevrimdisi');
        addLog('Baglanti hatasi: ' + error.message);
        return false;
    }
}

async function fetchCollections() {
    console.log('🔄 fetchCollections() called');
    try {
        const response = await fetch('/api/qdrant/collections');
        console.log('📡 Collections API response:', response.status);
        if (response.ok) {
            const data = await response.json();
            console.log('📦 Collections data:', data);
            const collections = data.result?.collections || [];

            // Fetch detailed info for each collection
            const detailedCollections = await Promise.all(
                collections.map(async (col) => {
                    try {
                        const detailResponse = await fetch(`/api/qdrant/collections/${col.name}`);
                        if (detailResponse.ok) {
                            const detailData = await detailResponse.json();
                            return {
                                name: col.name,
                                points_count: detailData.result?.points_count || 0,
                                vectors_count: detailData.result?.points_count || 0,
                                config: detailData.result?.config || {}
                            };
                        }
                    } catch (err) {
                        console.error(`Failed to fetch details for ${col.name}:`, err);
                    }
                    return { name: col.name, points_count: 0, vectors_count: 0, config: {} };
                })
            );

            displayCollections(detailedCollections);
            document.getElementById('stat-collections').textContent = collections.length;
            addLog(collections.length + ' collection yuklendi');
        }
    } catch (error) {
        addLog('Collection yukleme hatasi: ' + error.message);
    }
}

async function fetchClusterInfo() {
    try {
        const response = await fetch('/api/qdrant/cluster');
        if (response.ok) {
            const data = await response.json();
            displayHealthInfo(data.result);
        }
    } catch (error) {
        addLog('Cluster bilgisi alinamadi: ' + error.message);
    }
}

async function fetchTelemetry() {
    try {
        const response = await fetch('/api/qdrant/telemetry');
        if (response.ok) {
            const data = await response.json();
            updateStats(data.result);
        }
    } catch (error) {
        addLog(`⚠️ Telemetri bilgisi alınamadı: ${error.message}`);
    }
}

// ============================================
// UI Update Functions
// ============================================

function updateStatusBadge(status, text) {
    const badge = document.getElementById('qdrant-status');
    badge.className = `status-badge ${status}`;
    badge.querySelector('.status-text').textContent = text;
}

function updateStats(telemetry) {
    if (telemetry) {
        // Update statistics from telemetry data
        let totalVectors = 0;

        // Handle both array and object formats
        if (telemetry.collections) {
            if (Array.isArray(telemetry.collections)) {
                totalVectors = telemetry.collections.reduce((sum, col) => sum + (col.vectors_count || 0), 0);
            } else if (typeof telemetry.collections === 'object') {
                // Object format: convert to array
                totalVectors = Object.values(telemetry.collections).reduce((sum, col) => sum + (col.vectors_count || 0), 0);
            }
        }

        document.getElementById('stat-vectors').textContent = formatNumber(totalVectors);

        if (telemetry.app) {
            document.getElementById('stat-memory').textContent = formatBytes(telemetry.app.memory_usage || 0);
            document.getElementById('stat-status').textContent = telemetry.app.status || 'Aktif';
        }
    }
}

function displayCollections(collections) {
    console.log('🎨 displayCollections() called with:', collections);
    const container = document.getElementById('collections-list');
    console.log('📍 Container element:', container);

    if (collections.length === 0) {
        container.innerHTML = '<p class="loading-text">Henuz collection bulunmuyor</p>';
        return;
    }

    container.innerHTML = collections.map(col => `
        <div class="collection-card">
            <h3>📦 ${col.name}</h3>
            <p>Vektor Sayisi: ${formatNumber(col.vectors_count || 0)}</p>
            <p>Boyut: ${col.config?.params?.vectors?.size || 'N/A'}</p>
            <p>Mesafe: ${col.config?.params?.vectors?.distance || 'N/A'}</p>
            <div class="collection-actions">
                <button class="btn-info" onclick="showCollectionInfo('${col.name}')">ℹ️ Bilgi</button>
                <button class="btn-delete" onclick="deleteCollection('${col.name}')">🗑️ Sil</button>
            </div>
        </div>
    `).join('');
}

function displayHealthInfo(clusterInfo) {
    const container = document.getElementById('health-info');

    if (!clusterInfo) {
        container.innerHTML = '<p class="loading-text">Bilgi alınamadı</p>';
        return;
    }

    container.innerHTML = `
        <div class="info-row">
            <strong>Peer ID:</strong>
            <span>${clusterInfo.peer_id || 'N/A'}</span>
        </div>
        <div class="info-row">
            <strong>Raft Role:</strong>
            <span>${clusterInfo.raft_info?.role || 'Standalone'}</span>
        </div>
        <div class="info-row">
            <strong>Durum:</strong>
            <span style="color: var(--success);">✅ Sağlıklı</span>
        </div>
    `;
}

function addLog(message) {
    const container = document.getElementById('logs-container');
    const timestamp = new Date().toLocaleTimeString('tr-TR');
    const logEntry = document.createElement('p');
    logEntry.className = 'log-entry';
    logEntry.textContent = `[${timestamp}] ${message}`;
    container.insertBefore(logEntry, container.firstChild);

    // Keep only last 50 logs
    while (container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}

// ============================================
// Navigation
// ============================================

function setupNavigation() {
    const navLinks = document.querySelectorAll('.site-nav a[data-page]');
    const sidebarItems = document.querySelectorAll('.site-nav li');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageName = link.getAttribute('data-page');

            // Update active states
            sidebarItems.forEach(item => item.classList.remove('active'));
            link.parentElement.classList.add('active');

            // Show selected page
            showPage(pageName);
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page-content');
    pages.forEach(page => page.classList.remove('active'));

    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        document.getElementById('page-title').textContent = getTitleForPage(pageName);
        document.getElementById('current-page').textContent = getTitleForPage(pageName);

        // Load page-specific data
        loadPageData(pageName);
    }
}

function getTitleForPage(pageName) {
    const titles = {
        'dashboard': 'Qdrant Dashboard',
        'customers': 'Musteri Yonetimi',
        'collections': 'Collections',
        'status': 'Sistem Durumu',
        'logs': 'Loglar',
        'settings': 'Ayarlar'
    };
    return titles[pageName] || 'Dashboard';
}

function loadPageData(pageName) {
    switch (pageName) {
        case 'dashboard':
            refreshDashboard();
            break;
        case 'customers':
            if (typeof fetchCustomers === 'function') {
                fetchCustomers();
                fetchCustomerStats();
            }
            break;
        case 'collections':
            fetchCollections();
            break;
        case 'status':
            fetchClusterInfo();
            break;
    }
}

// ============================================
// Refresh & Auto-Update
// ============================================

async function refreshDashboard() {
    console.log('🔄 refreshDashboard() called');
    try {
        addLog('Dashboard yenileniyor...');
    } catch (e) {
        console.error('addLog error:', e);
    }

    try {
        await fetchQdrantStatus();
    } catch (e) {
        console.error('fetchQdrantStatus error:', e);
    }

    try {
        await fetchCollections();
    } catch (e) {
        console.error('fetchCollections error:', e);
    }

    try {
        await fetchTelemetry();
    } catch (e) {
        console.error('fetchTelemetry error:', e);
    }

    try {
        addLog('Dashboard guncellendi');
    } catch (e) {
        console.error('addLog error:', e);
    }
}

function startAutoRefresh() {
    const autoRefreshEl = document.getElementById('auto-refresh');
    if (!autoRefreshEl) {
        console.warn('⚠️ auto-refresh element not found, using default interval');
        return;
    }
    const interval = parseInt(autoRefreshEl.value) * 1000 || CONFIG.AUTO_REFRESH;

    if (state.autoRefreshInterval) {
        clearInterval(state.autoRefreshInterval);
    }

    state.autoRefreshInterval = setInterval(() => {
        if (state.isAuthenticated) {
            refreshDashboard();
        }
    }, interval);
}

// ============================================
// Utility Functions
// ============================================

function formatNumber(num) {
    return num.toLocaleString('tr-TR');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ============================================
// Initialization
// ============================================

function initDashboard() {
    console.log('🎬 initDashboard() called');
    setupNavigation();
    loadTheme();
    startAutoRefresh();
    refreshDashboard();
    console.log('✅ initDashboard() completed');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOMContentLoaded event fired');

    // Check if already authenticated
    const token = localStorage.getItem('auth_token');
    if (token) {
        // Verify token is still valid
        fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(res => {
            if (res.ok) {
                state.isAuthenticated = true;
                document.getElementById('login-overlay').classList.add('hidden');
                console.log('🔓 Token validated, auto-login successful');
                initDashboard();
            } else {
                // Token invalid, show login
                localStorage.removeItem('auth_token');
                document.getElementById('login-overlay').classList.remove('hidden');
            }
        })
        .catch(() => {
            localStorage.removeItem('auth_token');
            document.getElementById('login-overlay').classList.remove('hidden');
        });
    } else {
        // No token, show login
        document.getElementById('login-overlay').classList.remove('hidden');
    }

    // Login form
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;
        login(username, password);
    });

    // Theme toggle
    document.getElementById('theme-toggle-btn').addEventListener('click', toggleTheme);

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        if (confirm('Çıkış yapmak istediğinizden emin misiniz?')) {
            logout();
        }
    });

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', refreshDashboard);

    // Change password
    document.getElementById('change-password-btn').addEventListener('click', () => {
        const oldPass = prompt('Mevcut şifrenizi girin:');
        if (oldPass) {
            const newPass = prompt('Yeni şifrenizi girin:');
            if (newPass) {
                changePassword(oldPass, newPass);
            }
        }
    });

    // Auto-refresh settings
    document.getElementById('auto-refresh').addEventListener('change', startAutoRefresh);

    // Create collection button
    const createBtn = document.getElementById('create-collection-btn');
    if (createBtn) {
        createBtn.addEventListener('click', openCreateCollectionModal);
    }

    // Create collection form
    const createForm = document.getElementById('create-collection-form');
    if (createForm) {
        createForm.addEventListener('submit', handleCreateCollection);
    }
});

// ============================================
// Collection Management Functions
// ============================================

function openCreateCollectionModal() {
    document.getElementById('create-collection-modal').classList.add('show');
}

function closeCreateCollectionModal() {
    document.getElementById('create-collection-modal').classList.remove('show');
    document.getElementById('create-collection-form').reset();
}

async function handleCreateCollection(e) {
    e.preventDefault();

    const collectionName = document.getElementById('collection-name').value;
    const vectorSize = parseInt(document.getElementById('vector-size').value);
    const distanceMetric = document.getElementById('distance-metric').value;
    const onDiskPayload = document.getElementById('on-disk-payload').checked;

    // Validate collection name
    if (!/^[a-zA-Z0-9_-]+$/.test(collectionName)) {
        alert('Collection adi sadece harf, rakam, tire ve alt cizgi icermelidir!');
        return;
    }

    const config = {
        vectors: {
            size: vectorSize,
            distance: distanceMetric
        }
    };

    if (onDiskPayload) {
        config.on_disk_payload = true;
    }

    try {
        addLog('Collection olusturuluyor: ' + collectionName);

        const response = await fetch(`/api/qdrant/collections/${collectionName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            addLog('Collection basariyla olusturuldu: ' + collectionName);
            alert('Collection basariyla olusturuldu!');
            closeCreateCollectionModal();

            // Refresh collections list
            await fetchCollections();
        } else {
            const error = await response.json();
            addLog('Collection olusturma hatasi: ' + error.detail);
            alert('Hata: ' + error.detail);
        }
    } catch (error) {
        addLog('Collection olusturma hatasi: ' + error.message);
        alert('Hata: ' + error.message);
    }
}

async function deleteCollection(collectionName) {
    if (!confirm('Bu collection\'i silmek istediginizden emin misiniz?\n\n' + collectionName + '\n\nBu islem geri alinamaz!')) {
        return;
    }

    try {
        addLog('Collection siliniyor: ' + collectionName);

        const response = await fetch(`/api/qdrant/collections/${collectionName}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            addLog('Collection basariyla silindi: ' + collectionName);
            alert('Collection basariyla silindi!');

            // Refresh collections list
            await fetchCollections();
        } else {
            const error = await response.json();
            addLog('Collection silme hatasi: ' + error.detail);
            alert('Hata: ' + error.detail);
        }
    } catch (error) {
        addLog('Collection silme hatasi: ' + error.message);
        alert('Hata: ' + error.message);
    }
}

function showCollectionInfo(collectionName) {
    addLog('Collection bilgileri: ' + collectionName);
    alert('Collection detaylari:\n\n' + collectionName + '\n\n(Detayli goruntuleme ozelligi yakinda eklenecek)');
}

// Simple MD5 implementation (for demo purposes only)
const CryptoJS = {
    MD5: function(string) {
        function RotateLeft(lValue, iShiftBits) {
            return (lValue << iShiftBits) | (lValue >>> (32 - iShiftBits));
        }
        function AddUnsigned(lX, lY) {
            const lX8 = (lX & 0x80000000);
            const lY8 = (lY & 0x80000000);
            const lX4 = (lX & 0x40000000);
            const lY4 = (lY & 0x40000000);
            const lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF);
            if (lX4 & lY4) return (lResult ^ 0x80000000 ^ lX8 ^ lY8);
            if (lX4 | lY4) {
                if (lResult & 0x40000000) return (lResult ^ 0xC0000000 ^ lX8 ^ lY8);
                else return (lResult ^ 0x40000000 ^ lX8 ^ lY8);
            } else {
                return (lResult ^ lX8 ^ lY8);
            }
        }
        function F(x, y, z) { return (x & y) | ((~x) & z); }
        function G(x, y, z) { return (x & z) | (y & (~z)); }
        function H(x, y, z) { return (x ^ y ^ z); }
        function I(x, y, z) { return (y ^ (x | (~z))); }
        function FF(a, b, c, d, x, s, ac) {
            a = AddUnsigned(a, AddUnsigned(AddUnsigned(F(b, c, d), x), ac));
            return AddUnsigned(RotateLeft(a, s), b);
        }
        function GG(a, b, c, d, x, s, ac) {
            a = AddUnsigned(a, AddUnsigned(AddUnsigned(G(b, c, d), x), ac));
            return AddUnsigned(RotateLeft(a, s), b);
        }
        function HH(a, b, c, d, x, s, ac) {
            a = AddUnsigned(a, AddUnsigned(AddUnsigned(H(b, c, d), x), ac));
            return AddUnsigned(RotateLeft(a, s), b);
        }
        function II(a, b, c, d, x, s, ac) {
            a = AddUnsigned(a, AddUnsigned(AddUnsigned(I(b, c, d), x), ac));
            return AddUnsigned(RotateLeft(a, s), b);
        }
        function ConvertToWordArray(string) {
            let lWordCount;
            const lMessageLength = string.length;
            const lNumberOfWords_temp1 = lMessageLength + 8;
            const lNumberOfWords_temp2 = (lNumberOfWords_temp1 - (lNumberOfWords_temp1 % 64)) / 64;
            const lNumberOfWords = (lNumberOfWords_temp2 + 1) * 16;
            const lWordArray = Array(lNumberOfWords - 1);
            let lBytePosition = 0;
            let lByteCount = 0;
            while (lByteCount < lMessageLength) {
                lWordCount = (lByteCount - (lByteCount % 4)) / 4;
                lBytePosition = (lByteCount % 4) * 8;
                lWordArray[lWordCount] = (lWordArray[lWordCount] | (string.charCodeAt(lByteCount) << lBytePosition));
                lByteCount++;
            }
            lWordCount = (lByteCount - (lByteCount % 4)) / 4;
            lBytePosition = (lByteCount % 4) * 8;
            lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition);
            lWordArray[lNumberOfWords - 2] = lMessageLength << 3;
            lWordArray[lNumberOfWords - 1] = lMessageLength >>> 29;
            return lWordArray;
        }
        function WordToHex(lValue) {
            let WordToHexValue = "", WordToHexValue_temp = "", lByte, lCount;
            for (lCount = 0; lCount <= 3; lCount++) {
                lByte = (lValue >>> (lCount * 8)) & 255;
                WordToHexValue_temp = "0" + lByte.toString(16);
                WordToHexValue = WordToHexValue + WordToHexValue_temp.substr(WordToHexValue_temp.length - 2, 2);
            }
            return WordToHexValue;
        }
        const x = Array();
        let k, AA, BB, CC, DD, a, b, c, d;
        const S11 = 7, S12 = 12, S13 = 17, S14 = 22;
        const S21 = 5, S22 = 9, S23 = 14, S24 = 20;
        const S31 = 4, S32 = 11, S33 = 16, S34 = 23;
        const S41 = 6, S42 = 10, S43 = 15, S44 = 21;
        string = this.Utf8Encode(string);
        x = ConvertToWordArray(string);
        a = 0x67452301; b = 0xEFCDAB89; c = 0x98BADCFE; d = 0x10325476;
        for (k = 0; k < x.length; k += 16) {
            AA = a; BB = b; CC = c; DD = d;
            a = FF(a, b, c, d, x[k + 0], S11, 0xD76AA478);
            d = FF(d, a, b, c, x[k + 1], S12, 0xE8C7B756);
            c = FF(c, d, a, b, x[k + 2], S13, 0x242070DB);
            b = FF(b, c, d, a, x[k + 3], S14, 0xC1BDCEEE);
            a = FF(a, b, c, d, x[k + 4], S11, 0xF57C0FAF);
            d = FF(d, a, b, c, x[k + 5], S12, 0x4787C62A);
            c = FF(c, d, a, b, x[k + 6], S13, 0xA8304613);
            b = FF(b, c, d, a, x[k + 7], S14, 0xFD469501);
            a = FF(a, b, c, d, x[k + 8], S11, 0x698098D8);
            d = FF(d, a, b, c, x[k + 9], S12, 0x8B44F7AF);
            c = FF(c, d, a, b, x[k + 10], S13, 0xFFFF5BB1);
            b = FF(b, c, d, a, x[k + 11], S14, 0x895CD7BE);
            a = FF(a, b, c, d, x[k + 12], S11, 0x6B901122);
            d = FF(d, a, b, c, x[k + 13], S12, 0xFD987193);
            c = FF(c, d, a, b, x[k + 14], S13, 0xA679438E);
            b = FF(b, c, d, a, x[k + 15], S14, 0x49B40821);
            a = GG(a, b, c, d, x[k + 1], S21, 0xF61E2562);
            d = GG(d, a, b, c, x[k + 6], S22, 0xC040B340);
            c = GG(c, d, a, b, x[k + 11], S23, 0x265E5A51);
            b = GG(b, c, d, a, x[k + 0], S24, 0xE9B6C7AA);
            a = GG(a, b, c, d, x[k + 5], S21, 0xD62F105D);
            d = GG(d, a, b, c, x[k + 10], S22, 0x2441453);
            c = GG(c, d, a, b, x[k + 15], S23, 0xD8A1E681);
            b = GG(b, c, d, a, x[k + 4], S24, 0xE7D3FBC8);
            a = GG(a, b, c, d, x[k + 9], S21, 0x21E1CDE6);
            d = GG(d, a, b, c, x[k + 14], S22, 0xC33707D6);
            c = GG(c, d, a, b, x[k + 3], S23, 0xF4D50D87);
            b = GG(b, c, d, a, x[k + 8], S24, 0x455A14ED);
            a = GG(a, b, c, d, x[k + 13], S21, 0xA9E3E905);
            d = GG(d, a, b, c, x[k + 2], S22, 0xFCEFA3F8);
            c = GG(c, d, a, b, x[k + 7], S23, 0x676F02D9);
            b = GG(b, c, d, a, x[k + 12], S24, 0x8D2A4C8A);
            a = HH(a, b, c, d, x[k + 5], S31, 0xFFFA3942);
            d = HH(d, a, b, c, x[k + 8], S32, 0x8771F681);
            c = HH(c, d, a, b, x[k + 11], S33, 0x6D9D6122);
            b = HH(b, c, d, a, x[k + 14], S34, 0xFDE5380C);
            a = HH(a, b, c, d, x[k + 1], S31, 0xA4BEEA44);
            d = HH(d, a, b, c, x[k + 4], S32, 0x4BDECFA9);
            c = HH(c, d, a, b, x[k + 7], S33, 0xF6BB4B60);
            b = HH(b, c, d, a, x[k + 10], S34, 0xBEBFBC70);
            a = HH(a, b, c, d, x[k + 13], S31, 0x289B7EC6);
            d = HH(d, a, b, c, x[k + 0], S32, 0xEAA127FA);
            c = HH(c, d, a, b, x[k + 3], S33, 0xD4EF3085);
            b = HH(b, c, d, a, x[k + 6], S34, 0x4881D05);
            a = HH(a, b, c, d, x[k + 9], S31, 0xD9D4D039);
            d = HH(d, a, b, c, x[k + 12], S32, 0xE6DB99E5);
            c = HH(c, d, a, b, x[k + 15], S33, 0x1FA27CF8);
            b = HH(b, c, d, a, x[k + 2], S34, 0xC4AC5665);
            a = II(a, b, c, d, x[k + 0], S41, 0xF4292244);
            d = II(d, a, b, c, x[k + 7], S42, 0x432AFF97);
            c = II(c, d, a, b, x[k + 14], S43, 0xAB9423A7);
            b = II(b, c, d, a, x[k + 5], S44, 0xFC93A039);
            a = II(a, b, c, d, x[k + 12], S41, 0x655B59C3);
            d = II(d, a, b, c, x[k + 3], S42, 0x8F0CCC92);
            c = II(c, d, a, b, x[k + 10], S43, 0xFFEFF47D);
            b = II(b, c, d, a, x[k + 1], S44, 0x85845DD1);
            a = II(a, b, c, d, x[k + 8], S41, 0x6FA87E4F);
            d = II(d, a, b, c, x[k + 15], S42, 0xFE2CE6E0);
            c = II(c, d, a, b, x[k + 6], S43, 0xA3014314);
            b = II(b, c, d, a, x[k + 13], S44, 0x4E0811A1);
            a = II(a, b, c, d, x[k + 4], S41, 0xF7537E82);
            d = II(d, a, b, c, x[k + 11], S42, 0xBD3AF235);
            c = II(c, d, a, b, x[k + 2], S43, 0x2AD7D2BB);
            b = II(b, c, d, a, x[k + 9], S44, 0xEB86D391);
            a = AddUnsigned(a, AA); b = AddUnsigned(b, BB);
            c = AddUnsigned(c, CC); d = AddUnsigned(d, DD);
        }
        return (WordToHex(a) + WordToHex(b) + WordToHex(c) + WordToHex(d)).toLowerCase();
    },
    Utf8Encode: function(string) {
        string = string.replace(/\r\n/g, "\n");
        let utftext = "";
        for (let n = 0; n < string.length; n++) {
            const c = string.charCodeAt(n);
            if (c < 128) {
                utftext += String.fromCharCode(c);
            } else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            } else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }
        }
        return utftext;
    },
    toString: function() {
        return this.MD5;
    }
};
