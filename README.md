# 🎯 Qdrant Dashboard

Modern, şifreli ve tema destekli Qdrant Vector Database yönetim paneli.

## ✨ Özellikler

- 🔐 **Şifre Korumalı**: MD5 hash ile güvenli giriş sistemi
- 🌙 **Gece/Gündüz Modu**: Kullanıcı tercihine göre tema değiştirme
- 📊 **Dashboard**: Collection, vektör sayısı ve sistem durumu istatistikleri
- 📦 **Collection Yönetimi**: Collection listesi, oluşturma ve silme
- 💚 **Sistem Durumu**: Qdrant cluster ve health bilgileri
- 📋 **Log Takibi**: Tüm işlemlerin gerçek zamanlı log kaydı
- ⚙️ **Ayarlar**: Otomatik yenileme ve şifre değiştirme
- 🔄 **Otomatik Güncelleme**: Belirlenen aralıklarla otomatik veri güncelleme

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

## 🔑 Varsayılan Şifre

İlk girişte varsayılan şifre: **`password`**

Giriş yaptıktan sonra **Ayarlar** bölümünden şifrenizi değiştirebilirsiniz.

## 📁 Proje Yapısı

```
qdrant-dashboard/
├── app.py                      # FastAPI backend
├── requirements.txt            # Python bağımlılıkları
├── .env.example               # Örnek çevre değişkenleri
├── README.md                  # Bu dosya
├── templates/
│   └── index.html             # Ana dashboard HTML
├── static/
│   ├── css/
│   │   └── dashboard.css      # Stil dosyası (tema desteği)
│   └── js/
│       └── dashboard.js       # JavaScript (auth, tema, API)
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

### Dashboard API

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/` | Ana dashboard sayfası |
| `GET` | `/api/health` | API sağlık kontrolü |

### Qdrant Proxy API

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/qdrant/status` | Qdrant durumu |
| `GET` | `/api/qdrant/collections` | Tüm collection'lar |
| `GET` | `/api/qdrant/collections/{name}` | Collection detayı |
| `POST` | `/api/qdrant/collections/{name}` | Collection oluştur |
| `DELETE` | `/api/qdrant/collections/{name}` | Collection sil |
| `GET` | `/api/qdrant/cluster` | Cluster bilgisi |
| `GET` | `/api/qdrant/telemetry` | Telemetri verileri |
| `POST` | `/api/qdrant/collections/{name}/points/search` | Vektör arama |

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

## 🚀 Coolify Deployment

### Coolify'da Deploy

1. **New Resource** → **Docker Compose**
2. **Repository**: Bu projeyi bağla
3. **Environment Variables** ekle:
   - `QDRANT_URL=https://qdrant.turklawai.com`
   - `PORT=8080`
4. **Deploy** butonuna tıkla

### Docker Compose (Coolify)

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8080:8080"
    environment:
      - QDRANT_URL=https://qdrant.turklawai.com
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    restart: unless-stopped
```

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

## 📄 Lisans

Bu proje TurkLawAI projesi kapsamında geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için: [GitHub Issues](https://github.com/yourusername/qdrant-dashboard/issues)

---

**TurkLawAI** | Qdrant Dashboard v1.0.0
