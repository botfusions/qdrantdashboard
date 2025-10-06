# Coolify'da Qdrant Dashboard Deployment Rehberi

Bu rehber, Qdrant Dashboard'u Coolify üzerinde `https://qdrantdashboard.turklawai.com` adresiyle nasıl yayınlayacağınızı açıklar.

## 🚀 Hızlı Başlangıç

### 1. GitHub/GitLab Repository'ye Push Edin

Projeyi bir Git repository'sine push edin:

```bash
cd "C:\Users\user\Downloads\Project Claude\Qdrant arayüz\qdrant-dashboard"
git init
git add .
git commit -m "Initial commit: Qdrant Dashboard"
git remote add origin <REPOSITORY_URL>
git push -u origin main
```

### 2. Coolify'da Yeni Proje Oluşturun

1. Coolify dashboard'unuza giriş yapın
2. **"New Resource"** → **"Application"** seçin
3. Git repository URL'inizi girin
4. Branch: `main` (veya kullandığınız branch)
5. **"Continue"** butonuna tıklayın

### 3. Build Pack Ayarları

Coolify otomatik olarak Dockerfile'ı algılayacaktır:

- **Build Pack**: Dockerfile (Otomatik algılanır)
- **Dockerfile Path**: `./Dockerfile`
- **Port**: `8081`

### 4. Environment Variables (Çevre Değişkenleri)

Coolify'da **"Environment"** sekmesinden şu değişkenleri ekleyin:

```env
QDRANT_URL=https://qdrant.turklawai.com
QDRANT_API_KEY=PVrZ8QZkHrn4MFCvlZRhor1DMuoDr5l6
PORT=8081
SECRET_KEY=<GÜÇLÜ-BİR-SECRET-KEY-OLUŞTURUN>
```

**Önemli:** `SECRET_KEY` için güçlü bir anahtar oluşturun:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Domain Ayarları

1. Coolify'da **"Domains"** sekmesine gidin
2. **"Add Domain"** butonuna tıklayın
3. Domain adını girin: `qdrantdashboard.turklawai.com`
4. **"HTTPS"** seçeneğini aktif edin (Let's Encrypt otomatik SSL)
5. **"Save"** butonuna tıklayın

### 6. DNS Ayarları

Domain DNS ayarlarınızda A kaydı ekleyin:

```
Type: A
Name: qdrantdashboard (veya @ root için)
Value: <COOLIFY_SERVER_IP>
TTL: 3600
```

Cloudflare kullanıyorsanız:
1. Cloudflare DNS ayarlarına gidin
2. Yeni A kaydı ekleyin:
   - **Type**: A
   - **Name**: `qdrantdashboard`
   - **IPv4 address**: Coolify sunucu IP'niz
   - **Proxy status**: 🟠 DNS only (Proxied değil!)
   - **TTL**: Auto

### 7. Deploy Edin

1. Coolify'da **"Deploy"** butonuna tıklayın
2. Build loglarını izleyin
3. Deployment tamamlandığında `https://qdrantdashboard.turklawai.com` aktif olacak

## 📋 Post-Deployment Checklist

### İlk Giriş Bilgileri

Deployment sonrası ilk giriş için varsayılan kullanıcı:

- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`

⚠️ **ÖNEMLİ**: İlk girişten sonra mutlaka şifrenizi değiştirin!

### Health Check

Deployment sonrası test edin:

```bash
# Health check
curl https://qdrantdashboard.turklawai.com/api/health

# Beklenen cevap:
{"status":"healthy","qdrant_url":"https://qdrant.turklawai.com"}
```

### Güvenlik Kontrolleri

- [ ] `SECRET_KEY` güçlü bir değer olarak ayarlandı mı?
- [ ] Admin şifresi değiştirildi mi?
- [ ] HTTPS çalışıyor mu?
- [ ] Qdrant bağlantısı başarılı mı?

## 🔧 Volumes (Persistent Data)

Coolify'da **"Storages"** sekmesinden persistent volume'lar ekleyin:

```yaml
# users.json için
/app/users.json → /data/users.json

# customers.json için
/app/customers.json → /data/customers.json

# Data klasörü için
/app/data → /data/dashboard
```

Bu sayede container yeniden başlatıldığında kullanıcı ve müşteri bilgileri korunur.

## 🔄 Auto-Deployment (Otomatik Deployment)

Coolify'da **"Webhooks"** sekmesinden:

1. **"Git Auto Deploy"** seçeneğini aktif edin
2. GitHub/GitLab'da webhook URL'ini ekleyin
3. Artık her push'da otomatik deploy olacak

## 📊 Monitoring ve Logs

### Logs'ları İzleme

Coolify dashboard'da:
- **"Logs"** sekmesine gidin
- Real-time application logs'ları görün

### Resource Monitoring

- **CPU Usage**: %30'un altında olmalı (normal kullanımda)
- **Memory Usage**: ~500MB-1GB (embedding modeline bağlı)
- **Disk**: ~2GB (başlangıç için)

## 🐛 Troubleshooting (Sorun Giderme)

### Container Başlamıyor

1. Coolify logs'ları kontrol edin
2. Environment variables doğru mu?
3. Port 8081 açık mı?

```bash
# Container içinde test
docker exec -it <container_id> curl localhost:8081/api/health
```

### Domain Erişilemiyor

1. DNS propagation'ı bekleyin (15-30 dakika)
2. A kaydının doğru IP'ye işaret ettiğini kontrol edin
3. Cloudflare kullanıyorsanız Proxy'yi kapatın (DNS only)

### SSL Hatası

1. Let's Encrypt rate limit'e takılmış olabilir (1 saat bekleyin)
2. Domain DNS'i doğru mu?
3. Port 80 ve 443 açık mı?

## 🔐 Güvenlik Best Practices

### 1. Environment Variables'ı Güvenli Tutun

- `QDRANT_API_KEY` ve `SECRET_KEY` değerlerini asla Git'e commit etmeyin
- Coolify environment variables kullanın

### 2. Admin Şifresini Değiştirin

İlk giriş sonrası:
1. Dashboard'da **"Ayarlar"** → **"Şifre Değiştir"**
2. Güçlü bir şifre belirleyin

### 3. Network Security

- Sadece gerekli portları açın (80, 443)
- Firewall kurallarını ayarlayın
- Rate limiting kullanın (Cloudflare veya Coolify)

## 📈 Scaling ve Performance

### Embedding Model Optimizasyonu

`embedding_service.py` dosyasında model değiştirilebilir:

```python
# Daha hafif model için
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # ~90MB

# Daha güçlü model için (varsayılan)
model = SentenceTransformer('all-MiniLM-L6-v2')  # ~140MB
```

### Resource Limits (Coolify'da)

Coolify'da **"Resources"** sekmesinden:

```yaml
CPU: 1 core
Memory: 2GB
Disk: 10GB
```

## 🎯 Next Steps

Deployment başarılı olduktan sonra:

1. **Müşteri Ekleme**: Dashboard'dan yeni müşteriler ekleyin
2. **Collection Oluşturma**: Qdrant collection'ları yönetin
3. **Belge Yükleme**: PDF/TXT belgeler yükleyip embedding'leyin
4. **Monitoring**: Sistem durumunu düzenli kontrol edin

## 📞 Destek

Sorun yaşarsanız:
- Coolify logs'ları kontrol edin
- Health endpoint'i test edin: `/api/health`
- Container içine girin: `docker exec -it <container> bash`

---

**Hazırlayan**: Claude Code
**Tarih**: 2025-10-05
**Versiyon**: 2.0.0
