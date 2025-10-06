# Production customers.json Sync Rehberi

## 🎯 Amaç
Render.com ücretsiz planında shell erişimi olmadığı için, `customers.json` dosyasını güncellemek için API endpoint kullanıyoruz.

## ✅ Çözüm
Yeni eklenen **admin-only API endpoint** ile production'daki `customers.json` dosyasını güncelleyebilirsiniz.

## 📋 Adımlar

### 1️⃣ Render.com'da Deploy Bekleyin
GitHub'a push sonrası Render.com otomatik deploy başlatır. Deployment tamamlanana kadar bekleyin (2-3 dakika).

**Kontrol**: https://dashboard.render.com/web/qdrantdashboard

### 2️⃣ PowerShell Script Çalıştırın

Windows'da PowerShell açın:

```powershell
cd "C:\Users\user\Downloads\Project Claude\Qdrant arayüz\qdrant-dashboard"

# Script'i çalıştır
.\sync_customers_script.ps1
```

### 3️⃣ Sonuçları Kontrol Edin

Script şunları yapar:
1. ✅ Production'a login yapar (admin hesabı ile)
2. ✅ `customers.json` dosyasını okur
3. ✅ `/api/admin/sync-customers` endpoint'ine gönderir
4. ✅ Production'da dosyayı günceller
5. ✅ Backup oluşturur (`customers.json.backup`)
6. ✅ Customers listesini doğrular

**Beklenen Çıktı:**
```
🔐 Logging in to production dashboard...
✅ Login successful!

📤 Syncing customers.json to production...

📊 Sync Response:
{
  "success": true,
  "message": "Customers data synced successfully",
  "backup_created": "/app/customers.json.backup",
  "customers_count": 2,
  "customers": [...]
}

✅ Customers data synced successfully!
📊 Total customers: 2
💾 Backup created at: /app/customers.json.backup

🔍 Verifying customers list...

👥 Customers on production:
  - Volkan: customer_2122beac (134 documents)
  - Qdrant Customer: qdrant_customer_embedding (134 documents)
```

## 🔍 Doğrulama

### Dashboard'da Kontrol
1. https://qdrantdashboard.turklawai.com açın
2. Login yapın (admin / Ce848005/1)
3. **2 customer** görünmeli:
   - Volkan (134 document)
   - Qdrant Customer (134 document)

### API ile Kontrol
```powershell
# Login
$login = Invoke-RestMethod -Uri "https://qdrantdashboard.turklawai.com/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Ce848005/1"}'

$token = $login.access_token

# Customers listesi
Invoke-RestMethod -Uri "https://qdrantdashboard.turklawai.com/api/customers" `
  -Method GET `
  -Headers @{"Authorization"="Bearer $token"} `
  | ConvertTo-Json -Depth 10
```

## 🛡️ Güvenlik

- ✅ **Admin-only**: Sadece admin rolündeki kullanıcılar sync yapabilir
- ✅ **JWT Authentication**: Token tabanlı güvenlik
- ✅ **Automatic Backup**: Her sync öncesi otomatik yedek
- ✅ **Rollback on Error**: Hata durumunda otomatik geri alma

## 📝 API Endpoint Detayları

### Endpoint
```
POST /api/admin/sync-customers
```

### Authentication
```
Authorization: Bearer <JWT_TOKEN>
```

### Request Body
```json
{
  "customers": [
    {
      "customer_id": "2122beac",
      "name": "Volkan",
      "email": "selam@sandaluci.com",
      "quota_mb": 100,
      "used_mb": 0.01,
      "collection_name": "customer_2122beac",
      "created_at": "2025-09-30T19:28:49.018839",
      "active": true,
      "document_count": 134,
      "last_upload": "2025-10-06T00:00:00",
      "usage_percent": 0.01,
      "remaining_mb": 99.99
    },
    {
      "customer_id": "qdrant_main",
      "name": "Qdrant Customer",
      "email": "qdrant@turklawai.com",
      "collection_name": "qdrant_customer_embedding",
      "quota_mb": 1000,
      "used_mb": 0,
      "document_count": 134,
      "created_at": "2025-10-01T00:00:00",
      "updated_at": "2025-10-06T20:09:49.751226",
      "active": true
    }
  ]
}
```

### Response (Success)
```json
{
  "success": true,
  "message": "Customers data synced successfully",
  "backup_created": "/app/customers.json.backup",
  "customers_count": 2,
  "customers": [...]
}
```

### Response (Error)
```json
{
  "detail": "Failed to sync customers: <error_message>"
}
```

## 🚨 Troubleshooting

### Sorun: "Login failed"
**Çözüm**: Production şifresini kontrol edin (`Ce848005/1`)

### Sorun: "403 Forbidden"
**Çözüm**: Admin rolü gereklidir. Sadece admin kullanıcısı sync yapabilir.

### Sorun: "Invalid data format"
**Çözüm**: `customers.json` formatını kontrol edin. `{"customers": [...]}` yapısında olmalı.

### Sorun: Script hata veriyor
**Çözüm**:
1. Render.com deployment tamamlandı mı kontrol edin
2. `customers.json` dosyası mevcut mu kontrol edin
3. Internet bağlantınızı kontrol edin

## 📚 Alternatif Yöntemler

### Bash Script (Linux/Mac)
```bash
chmod +x sync_customers_script.sh
./sync_customers_script.sh
```

### Manuel cURL (Her Platformda)
```bash
# 1. Login
TOKEN=$(curl -s -X POST "https://qdrantdashboard.turklawai.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Ce848005/1"}' \
  | jq -r '.access_token')

# 2. Sync
curl -X POST "https://qdrantdashboard.turklawai.com/api/admin/sync-customers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @customers.json
```

## ✅ Başarı Kriterleri

Sync başarılı olduysa:
- ✅ Script "success: true" döner
- ✅ Dashboard'da 2 customer görünür
- ✅ Her customer'ın 134 document'i vardır
- ✅ Collection isimleri doğrudur:
  - Volkan → `customer_2122beac`
  - Qdrant Customer → `qdrant_customer_embedding`

## 📅 Son Güncelleme
06.10.2025 - Admin sync endpoint eklendi
