# Production customers.json Güncelleme Talimatları

## Sorun
Volkan müşterisi dashboard'da gözükmüyor çünkü production'daki `customers.json` dosyası güncel değil.

## Qdrant Collection Durumu
```bash
# Qdrant'ta 3 collection var:
1. customer_2122beac → 134 vektör (Volkan'ın orijinal collection'ı)
2. qdrant_customer_embedding → 134 vektör (Yeni oluşturulan collection)
3. documents → Başka bir collection
```

## Çözüm

### Yöntem 1: Render.com Shell (Önerilen)

1. **Render.com'a giriş yapın**: https://dashboard.render.com
2. **qdrantdashboard** servisine gidin
3. **Shell** sekmesine tıklayın
4. Aşağıdaki komutları çalıştırın:

```bash
# Mevcut dosyayı yedekle
cp customers.json customers.json.backup

# Dosyayı düzenle
cat > customers.json << 'EOF'
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
EOF

# Doğrula
cat customers.json

# Servisi yeniden başlat (opsiyonel)
# Render otomatik algılar ve reload eder
```

### Yöntem 2: Environment Variable (Alternatif)

Render.com → Environment sekmesi → Add Environment Variable:

**Name**: `CUSTOMERS_JSON_CONTENT`
**Value**: (customers.json dosyasının tamamı)

Sonra `app.py`'de startup'ta bu env var'dan customers.json oluştur.

### Yöntem 3: Persistent Volume Kullanımı

Render.com persistent disk özelliği varsa:
1. `/data` dizinini persistent disk olarak tanımla
2. `customers.json` ve `users.json` dosyalarını `/data` dizinine taşı
3. Uygulama bu dizinden okusun

## Doğrulama

Güncelleme sonrası kontrol:

```bash
# API'den customers listesini al
curl https://qdrantdashboard.turklawai.com/api/customers

# Yanıt:
# {
#   "customers": [...],
#   "total": 2  ← Bu 2 olmalı (Volkan + Qdrant Customer)
# }
```

Dashboard'da görmek için:
1. https://qdrantdashboard.turklawai.com açın
2. Login yapın
3. Customers sekmesinde **2 customer** görünmeli:
   - Volkan (134 document)
   - Qdrant Customer (134 document)

## Notlar

- `customers.json` dosyası `.gitignore`'da olduğu için GitHub'a push edilmiyor
- Production'da manuel güncelleme gerekiyor
- `customers.json.example` dosyası güncel hale getirildi (GitHub'da mevcut)
- Her iki collection da Qdrant'ta mevcut ve aktif
