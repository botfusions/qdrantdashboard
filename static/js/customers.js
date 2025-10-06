// Customer Management JavaScript Functions

// ============================================
// Fetch Customers
// ============================================

async function fetchCustomers() {
    try {
        const response = await fetch('/api/customers');
        if (response.ok) {
            const data = await response.json();
            displayCustomers(data.customers || []);
            addLog((data.customers?.length || 0) + ' musteri yuklendi');
        }
    } catch (error) {
        addLog('Musteri yukleme hatasi: ' + error.message);
    }
}

async function fetchCustomerStats() {
    try {
        const response = await fetch('/api/customers/stats');
        if (response.ok) {
            const stats = await response.json();
            updateCustomerStats(stats);
        }
    } catch (error) {
        console.error('Stats yukleme hatasi:', error);
    }
}

function updateCustomerStats(stats) {
    document.getElementById('total-customers-count').textContent = stats.total_customers || 0;
    document.getElementById('active-customers-count').textContent = stats.active_customers || 0;
    document.getElementById('total-documents-count').textContent = formatNumber(stats.total_documents || 0);
    document.getElementById('total-usage-mb').textContent = stats.total_used_mb.toFixed(2) + ' MB';
}

function displayCustomers(customers) {
    const container = document.getElementById('customers-list');

    if (customers.length === 0) {
        container.innerHTML = '<p class="loading-text">Henuz musteri bulunmuyor. Yeni musteri ekleyerek baslayabilirsiniz.</p>';
        return;
    }

    container.innerHTML = customers.map(customer => {
        const usagePercent = customer.usage_percent || 0;
        const progressClass = usagePercent > 90 ? 'danger' : usagePercent > 70 ? 'warning' : '';

        return `
            <div class="customer-card">
                <div class="customer-card-header">
                    <div class="customer-info">
                        <h3>${customer.name}</h3>
                        <p class="email">${customer.email}</p>
                        <small>ID: ${customer.customer_id} | Collection: ${customer.collection_name}</small>
                    </div>
                    <span class="customer-badge ${customer.active ? 'active' : 'inactive'}">
                        ${customer.active ? 'Aktif' : 'Pasif'}
                    </span>
                </div>

                <div class="customer-stats-row">
                    <div class="customer-stat">
                        <strong>${customer.document_count || 0}</strong>
                        <span>Belge</span>
                    </div>
                    <div class="customer-stat">
                        <strong>${customer.used_mb.toFixed(2)} MB</strong>
                        <span>Kullanimda</span>
                    </div>
                    <div class="customer-stat">
                        <strong>${customer.remaining_mb.toFixed(2)} MB</strong>
                        <span>Kalan</span>
                    </div>
                    <div class="customer-stat">
                        <strong>${customer.quota_mb} MB</strong>
                        <span>Toplam Kota</span>
                    </div>
                </div>

                <div class="quota-progress">
                    <div class="quota-progress-label">
                        <span>Kota Kullanimi</span>
                        <strong>${usagePercent.toFixed(1)}%</strong>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${progressClass}" style="width: ${usagePercent}%"></div>
                    </div>
                </div>

                <div class="customer-actions">
                    <button class="btn-upload" onclick="openUploadModal('${customer.customer_id}')">
                        Belge Yukle
                    </button>
                    <button class="btn-info" onclick="showCustomerInfo('${customer.customer_id}')">
                        Detaylar
                    </button>
                    <button class="btn-delete" onclick="deleteCustomer('${customer.customer_id}')">
                        Sil
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// ============================================
// Create Customer
// ============================================

function openCreateCustomerModal() {
    document.getElementById('create-customer-modal').classList.add('show');
}

function closeCreateCustomerModal() {
    document.getElementById('create-customer-modal').classList.remove('show');
    document.getElementById('create-customer-form').reset();
}

async function handleCreateCustomer(e) {
    e.preventDefault();

    const name = document.getElementById('customer-name').value;
    const email = document.getElementById('customer-email').value;
    const quotaMb = parseInt(document.getElementById('customer-quota').value);

    try {
        addLog('Musteri olusturuluyor: ' + name);

        const response = await fetch('/api/customers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                quota_mb: quotaMb
            })
        });

        if (response.ok) {
            const result = await response.json();
            addLog('Musteri basariyla olusturuldu: ' + result.customer.customer_id);
            alert('Musteri basariyla olusturuldu!\n\nID: ' + result.customer.customer_id + '\nCollection: ' + result.customer.collection_name);
            closeCreateCustomerModal();

            // Refresh customers list
            await fetchCustomers();
            await fetchCustomerStats();
        } else {
            const error = await response.json();
            addLog('Musteri olusturma hatasi: ' + error.detail);
            alert('Hata: ' + error.detail);
        }
    } catch (error) {
        addLog('Musteri olusturma hatasi: ' + error.message);
        alert('Hata: ' + error.message);
    }
}

// ============================================
// Upload Document
// ============================================

function openUploadModal(customerId) {
    // Get customer info
    fetch(`/api/customers/${customerId}`)
        .then(res => res.json())
        .then(customer => {
            document.getElementById('upload-customer-id').value = customerId;
            document.getElementById('upload-customer-name').textContent = customer.name;
            document.getElementById('upload-remaining-quota').textContent = customer.remaining_mb.toFixed(1) + ' MB';
            document.getElementById('upload-document-modal').classList.add('show');
        })
        .catch(error => {
            alert('Musteri bilgileri alinamadi: ' + error.message);
        });
}

function closeUploadModal() {
    document.getElementById('upload-document-modal').classList.remove('show');
    document.getElementById('upload-document-form').reset();
}

async function handleUploadDocument(e) {
    e.preventDefault();

    const customerId = document.getElementById('upload-customer-id').value;
    const fileInput = document.getElementById('document-file');
    const description = document.getElementById('document-description').value;

    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Lutfen bir dosya secin!');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
        formData.append('description', description);
    }

    try {
        addLog('Belge yukleniyor: ' + file.name);

        const response = await fetch(`/api/customers/${customerId}/upload`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            addLog('Belge basariyla yuklendi: ' + result.file_name);
            alert('Belge basariyla yuklendi!\n\nDosya: ' + result.file_name + '\nBoyut: ' + result.size_mb + ' MB');
            closeUploadModal();

            // Refresh customers list
            await fetchCustomers();
            await fetchCustomerStats();
        } else {
            const error = await response.json();
            addLog('Belge yukleme hatasi: ' + error.detail);
            alert('Hata: ' + error.detail);
        }
    } catch (error) {
        addLog('Belge yukleme hatasi: ' + error.message);
        alert('Hata: ' + error.message);
    }
}

// ============================================
// Delete Customer
// ============================================

async function deleteCustomer(customerId) {
    const customer = await fetch(`/api/customers/${customerId}`).then(res => res.json());

    if (!confirm('Bu musteriyi silmek istediginizden emin misiniz?\n\nMusteri: ' + customer.name + '\nEmail: ' + customer.email + '\n\nBu islem geri alinamaz ve tum belgeleri silinecektir!')) {
        return;
    }

    try {
        addLog('Musteri siliniyor: ' + customerId);

        const response = await fetch(`/api/customers/${customerId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            addLog('Musteri basariyla silindi: ' + customerId);
            alert('Musteri basariyla silindi!');

            // Refresh customers list
            await fetchCustomers();
            await fetchCustomerStats();
        } else {
            const error = await response.json();
            addLog('Musteri silme hatasi: ' + error.detail);
            alert('Hata: ' + error.detail);
        }
    } catch (error) {
        addLog('Musteri silme hatasi: ' + error.message);
        alert('Hata: ' + error.message);
    }
}

// ============================================
// Show Customer Info
// ============================================

function showCustomerInfo(customerId) {
    Promise.all([
        fetch(`/api/customers/${customerId}`).then(res => res.json()),
        fetch(`/api/customers/${customerId}/documents`).then(res => res.json())
    ])
    .then(([customer, documents]) => {
        let docList = '\n\nYuklenmis Belgeler:\n';
        if (documents.documents && documents.documents.length > 0) {
            documents.documents.forEach(doc => {
                docList += `\n- ${doc.filename} (${doc.chunks} chunk, ${doc.file_size_mb.toFixed(2)} MB)`;
            });
            docList += `\n\nToplam: ${documents.total_documents} belge, ${documents.total_chunks} chunk`;
        } else {
            docList += '\nHenuz belge yuklenmemis';
        }

        const info = `
Musteri Detaylari:

ID: ${customer.customer_id}
Ad: ${customer.name}
Email: ${customer.email}
Collection: ${customer.collection_name}

Kota: ${customer.quota_mb} MB
Kullanim: ${customer.used_mb.toFixed(2)} MB (${customer.usage_percent}%)
Kalan: ${customer.remaining_mb.toFixed(2)} MB

Belge Sayisi: ${customer.document_count}
Durum: ${customer.active ? 'Aktif' : 'Pasif'}
Kayit Tarihi: ${new Date(customer.created_at).toLocaleString('tr-TR')}
Son Yukleme: ${customer.last_upload ? new Date(customer.last_upload).toLocaleString('tr-TR') : 'Henuz yukleme yapilmamis'}
${docList}
        `;
        alert(info);
    })
    .catch(error => {
        alert('Musteri bilgileri alinamadi: ' + error.message);
    });
}

// ============================================
// Event Listeners
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Create customer button
    const createCustomerBtn = document.getElementById('create-customer-btn');
    if (createCustomerBtn) {
        createCustomerBtn.addEventListener('click', openCreateCustomerModal);
    }

    // Create customer form
    const createCustomerForm = document.getElementById('create-customer-form');
    if (createCustomerForm) {
        createCustomerForm.addEventListener('submit', handleCreateCustomer);
    }

    // Upload document form
    const uploadForm = document.getElementById('upload-document-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadDocument);
    }

    // Collection name preview
    const customerNameInput = document.getElementById('customer-name');
    const collectionPreview = document.getElementById('collection-name-preview');
    if (customerNameInput && collectionPreview) {
        customerNameInput.addEventListener('input', (e) => {
            const name = e.target.value.toLowerCase().trim().replace(/\s+/g, '_');
            if (name) {
                collectionPreview.textContent = `${name}_document`;
                collectionPreview.style.color = '#2c3e50';
            } else {
                collectionPreview.textContent = '{ad}_document';
                collectionPreview.style.color = '#666';
            }
        });
    }
});
