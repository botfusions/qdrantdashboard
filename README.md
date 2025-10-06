# 🎯 Qdrant Dashboard

Modern, multi-tenant Qdrant Vector Database yönetim paneli. JWT authentication, customer management ve production-ready deployment özellikleri ile.

## 🌐 Live Demo

**Production URL**: https://qdrantdashboard.turklawai.com
**Login**: admin / admin123

## ✨ Özellikler

### Core Features
- 🔐 **JWT Authentication**: Güvenli token-based authentication
- 👥 **Multi-Tenant Support**: Customer bazlı quota ve collection yönetimi
- 📊 **Dashboard**: Collection, vektör sayısı ve sistem durumu istatistikleri
- 📦 **Collection Yönetimi**: Collection listesi, oluşturma ve silme
- 💚 **Sistem Durumu**: Qdrant cluster ve health bilgileri
- 📋 **Real-time Stats**: Customer usage, quota tracking
- ⚙️ **Admin Panel**: User management, customer operations
- 🔄 **Auto-Deploy**: GitHub push → Production deployment

### Advanced Features (06.10.2025)
- 🔧 **Admin Sync Endpoint**: Remote `customers.json` update without shell access
- 🛡️ **Auto Backup**: Automatic backup before data sync
- 🔄 **Error Rollback**: Automatic rollback on sync failure
- 📜 **PowerShell/Bash Scripts**: Automated sync workflows
- 🌙 **Theme Support**: Dark/Light mode (preserved from v1.0)

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 2. Çevre Değişkenlerini Ayarla

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
QDRANT_URL=https://qdrant.turklawai.com
QDRANT_API_KEY=your_api_key_here  # Opsiyonel
PORT=8080
```

### 3. Uygulamayı Başlat

```bash
python app.py
```

veya

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

Dashboard `http://localhost:8080` adresinde çalışacaktır.

## 🔑 Varsayılan Credentials

**Username**: admin
**Password**: admin123

⚠️ **Production'da şifrenizi mutlaka değiştirin!**

## 📁 Proje Yapısı

```
qdrant-dashboard/
├── app.py                          # FastAPI backend + Admin sync endpoint
├── auth.py                         # JWT authentication
├── customer_manager.py             # Customer operations
├── embedding_service.py            # Embedding service
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── customers.json                  # Customer database (gitignored)
├── users.json                      # User database (gitignored)
├── Dockerfile                      # Production container
├── docker-compose.yml              # Docker compose config
├── README.md                       # This file
├── TODO.md                         # Task tracking
├── SUCCESS_SUMMARY.md              # Latest success report
├── PRODUCTION_SYNC_GUIDE.md        # Sync guide
├── NEXT_STEPS.md                   # Roadmap
├── sync_customers_script.ps1       # PowerShell sync automation
├── sync_customers_script.sh        # Bash sync automation
├── reset_admin_password.py         # Password reset utility
├── templates/
│   └── index.html                 # Dashboard UI
└── static/
    ├── css/
    │   └── dashboard.css          # Styling
    └── js/
        ├── dashboard.js           # Main logic + auth
        └── customers.js           # Customer management
```

## 🎨 Tema Sistemi

Dashboard otomatik olarak tema tercihini `localStorage` ile kaydeder:

- **Gündüz Modu**: Açık renkler, beyaz arka plan
- **Gece Modu**: Koyu renkler, siyah arka plan

Tema değiştirme sol menüdeki "Tema Değiştir" butonundan yapılır.

## 🔒 Güvenlik

### Şifre Hash

- Şifreler MD5 hash ile saklanır (demo amaçlı)
- Prodüksiyon için bcrypt veya Argon2 kullanılmalı

### Şifre Değiştirme

1. Dashboard'a giriş yapın
2. **Ayarlar** sayfasına gidin
3. "🔑 Şifre Değiştir" butonuna tıklayın
4. Mevcut şifrenizi girin
5. Yeni şifrenizi girin

Şifre değişikliği `localStorage` üzerinde saklanır.

## 📊 API Endpoints

### Authentication API

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| `POST` | `/api/auth/login` | JWT token al | - |
| `POST` | `/api/auth/logout` | Logout | JWT |
| `POST` | `/api/auth/change-password` | Şifre değiştir | JWT |
| `GET` | `/api/auth/me` | Kullanıcı bilgisi | JWT |

### Customer Management API

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| `GET` | `/api/customers` | Customer listesi | JWT |
| `GET` | `/api/customers/stats` | Customer istatistikleri | JWT |
| `GET` | `/api/customers/{id}` | Customer detayı | JWT |
| `POST` | `/api/customers` | Yeni customer | JWT |
| `PUT` | `/api/customers/{id}` | Customer güncelle | JWT |
| `DELETE` | `/api/customers/{id}` | Customer sil | JWT |
| `POST` | `/api/customers/{id}/upload` | File upload | JWT |
| `GET` | `/api/customers/{id}/documents` | Document listesi | JWT |

### Admin API (New! 06.10.2025)

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| `POST` | `/api/admin/sync-customers` | customers.json sync | Admin JWT |

**Sync Endpoint Özellikleri**:
- ✅ Admin-only (role: admin)
- ✅ Automatic backup (`customers.json.backup`)
- ✅ Data validation
- ✅ Error rollback
- ✅ Returns customer count

**Usage**:
```bash
# Login
TOKEN=$(curl -X POST https://qdrantdashboard.turklawai.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Sync customers
curl -X POST https://qdrantdashboard.turklawai.com/api/admin/sync-customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @customers.json
```

### Qdrant Proxy API

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| `GET` | `/api/qdrant/status` | Qdrant durumu | - |
| `GET` | `/api/qdrant/collections` | Tüm collection'lar | - |
| `GET` | `/api/qdrant/collections/{name}` | Collection detayı | - |
| `POST` | `/api/qdrant/collections/{name}` | Collection oluştur | JWT |
| `DELETE` | `/api/qdrant/collections/{name}` | Collection sil | JWT |
| `GET` | `/api/qdrant/cluster` | Cluster bilgisi | - |
| `GET` | `/api/qdrant/telemetry` | Telemetri verileri | - |

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
```

Build ve çalıştırma:

```bash
docker build -t qdrant-dashboard .
docker run -p 8080:8080 \
  -e QDRANT_URL=https://qdrant.turklawai.com \
  qdrant-dashboard
```

## 🚀 Production Deployment

### Render.com (Current Production)

**Live URL**: https://qdrantdashboard.turklawai.com

**Auto-Deploy Setup**:
1. Fork/Import GitHub repo
2. Create new Web Service
3. Set environment variables:
   - `QDRANT_URL=https://qdrant.turklawai.com`
   - `QDRANT_API_KEY=<your_key>`
   - `PORT=8081`
4. Deploy → Automatic SSL + Custom domain

**Sync customers.json** (no shell access needed):
```powershell
# Windows
.\sync_customers_script.ps1

# Linux/Mac
./sync_customers_script.sh
```

### Coolify Deployment (Alternative)

1. **New Resource** → **Docker Compose**
2. **Repository**: Connect this project
3. **Environment Variables**:
   - `QDRANT_URL=https://qdrant.turklawai.com`
   - `QDRANT_API_KEY=<your_key>`
   - `PORT=8081`
4. **Deploy** → Auto SSL with Let's Encrypt

See `COOLIFY_DEPLOYMENT.md` for detailed instructions.

## 📝 Özelleştirme

### Varsayılan Şifreyi Değiştirme

`static/js/dashboard.js` dosyasında:

```javascript
const CONFIG = {
    PASSWORD_HASH: 'your_md5_hash_here', // Yeni şifrenin MD5 hash'i
    // ...
};
```

MD5 hash oluşturma (Python):

```python
import hashlib
password = "yeni_şifre"
hash_value = hashlib.md5(password.encode()).hexdigest()
print(hash_value)
```

### Otomatik Yenileme Süresi

`static/js/dashboard.js` dosyasında:

```javascript
const CONFIG = {
    AUTO_REFRESH: 30000, // 30 saniye (milisaniye cinsinden)
    // ...
};
```

## 🛠️ Geliştirme

### Hot Reload ile Çalıştırma

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Debug Modu

```bash
PYTHONDONTWRITEBYTECODE=1 python app.py
```

## 📚 Documentation

- **README.md** - This file (main documentation)
- **TODO.md** - Task tracking and completed features
- **SUCCESS_SUMMARY.md** - Latest success report (Volkan customer fix)
- **PRODUCTION_SYNC_GUIDE.md** - Production sync instructions
- **UPDATE_PRODUCTION.md** - Problem analysis and solutions
- **NEXT_STEPS.md** - Roadmap and future features
- **COOLIFY_DEPLOYMENT.md** - Coolify deployment guide

## 🎯 Recent Updates (06.10.2025)

### ✅ Volkan Customer Fix - COMPLETED
- **Problem**: Customer not visible on dashboard
- **Root Cause**: Production `customers.json` out of sync
- **Solution**: Admin API endpoint for remote sync
- **Status**: ✅ SOLVED - Both customers now visible (Volkan + Qdrant Customer)

### 🆕 New Features
- **Admin Sync Endpoint**: `POST /api/admin/sync-customers`
- **Automation Scripts**: PowerShell/Bash sync automation
- **Auto Backup**: Backup before every sync
- **Error Recovery**: Automatic rollback on failure

See `SUCCESS_SUMMARY.md` for complete details.

## 📄 Lisans

Bu proje TurkLawAI projesi kapsamında geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

- **GitHub**: https://github.com/botfusions/qdrantdashboard
- **Issues**: https://github.com/botfusions/qdrantdashboard/issues
- **Production**: https://qdrantdashboard.turklawai.com

---

**TurkLawAI** | Qdrant Dashboard v2.0.0 (06.10.2025)
