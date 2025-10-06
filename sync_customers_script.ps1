# Qdrant Dashboard - Production customers.json Sync Script (PowerShell)
# Bu script ile Render.com'da shell erişimi olmadan customers.json güncellenebilir

$PRODUCTION_URL = "https://qdrantdashboard.turklawai.com"
$ADMIN_PASSWORD = "Ce848005/1"

Write-Host "🔐 Logging in to production dashboard..." -ForegroundColor Cyan

# Login ve token al
$loginBody = @{
    username = "admin"
    password = $ADMIN_PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$PRODUCTION_URL/api/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody

    $TOKEN = $loginResponse.access_token

    if (-not $TOKEN) {
        Write-Host "❌ Login failed! Check your password." -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📤 Syncing customers.json to production..." -ForegroundColor Cyan

    # customers.json içeriğini oku
    $customersJson = Get-Content -Path "customers.json" -Raw

    # Sync endpoint'ine gönder
    $headers = @{
        "Authorization" = "Bearer $TOKEN"
        "Content-Type" = "application/json"
    }

    $syncResponse = Invoke-RestMethod -Uri "$PRODUCTION_URL/api/admin/sync-customers" `
        -Method POST `
        -Headers $headers `
        -Body $customersJson

    # Sonucu göster
    Write-Host ""
    Write-Host "📊 Sync Response:" -ForegroundColor Yellow
    $syncResponse | ConvertTo-Json -Depth 10

    if ($syncResponse.success -eq $true) {
        Write-Host ""
        Write-Host "✅ Customers data synced successfully!" -ForegroundColor Green
        Write-Host "📊 Total customers: $($syncResponse.customers_count)" -ForegroundColor Cyan
        Write-Host "💾 Backup created at: $($syncResponse.backup_created)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔍 Verifying customers list..." -ForegroundColor Cyan

        # Customers listesini doğrula
        $customersResponse = Invoke-RestMethod -Uri "$PRODUCTION_URL/api/customers" `
            -Method GET `
            -Headers $headers

        Write-Host ""
        Write-Host "👥 Customers on production:" -ForegroundColor Yellow
        $customersResponse.customers | ForEach-Object {
            Write-Host "  - $($_.name): $($_.collection_name) ($($_.document_count) documents)" -ForegroundColor White
        }
    }
    else {
        Write-Host ""
        Write-Host "❌ Sync failed!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
