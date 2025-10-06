#!/bin/bash

# Qdrant Dashboard - Production customers.json Sync Script
# Bu script ile Render.com'da shell erişimi olmadan customers.json güncellenebilir

PRODUCTION_URL="https://qdrantdashboard.turklawai.com"
ADMIN_PASSWORD="Ce848005/1"

echo "🔐 Logging in to production dashboard..."

# Login ve token al
TOKEN=$(curl -s -X POST "$PRODUCTION_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$ADMIN_PASSWORD\"}" \
  | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Check your password."
    exit 1
fi

echo "✅ Login successful!"
echo ""
echo "📤 Syncing customers.json to production..."

# customers.json içeriğini oku ve API'ye gönder
CUSTOMERS_DATA=$(cat customers.json)

# Sync endpoint'ine gönder
RESPONSE=$(curl -s -X POST "$PRODUCTION_URL/api/admin/sync-customers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "$CUSTOMERS_DATA")

# Sonucu göster
echo "$RESPONSE" | jq '.'

# Başarıyı kontrol et
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "✅ Customers data synced successfully!"
    echo "📊 Total customers:" $(echo "$RESPONSE" | jq -r '.customers_count')
    echo "💾 Backup created at:" $(echo "$RESPONSE" | jq -r '.backup_created')
    echo ""
    echo "🔍 Verifying customers list..."

    # Customers listesini doğrula
    curl -s "$PRODUCTION_URL/api/customers" \
      -H "Authorization: Bearer $TOKEN" \
      | jq '.customers[] | {name, collection_name, document_count}'
else
    echo ""
    echo "❌ Sync failed!"
    exit 1
fi
