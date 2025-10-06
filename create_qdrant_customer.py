#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create customer entry for qdrant_customer_embedding collection
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

customer_data = {
    "customer_id": "qdrant_main",
    "name": "Qdrant Customer",
    "email": "qdrant@turklawai.com",
    "collection_name": "qdrant_customer_embedding",
    "quota_mb": 1000,
    "used_mb": 0,  # Will be calculated from Qdrant
    "document_count": 2,  # Based on your data
    "created_at": "2025-10-01T00:00:00",
    "updated_at": datetime.utcnow().isoformat(),
    "active": True
}

customers_file = Path(__file__).parent / "customers.json"

print(f"[*] Creating customer entry for qdrant_customer_embedding...")

try:
    with open(customers_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if it's array or dict format
    if isinstance(data, dict) and 'customers' in data:
        # New format: {"customers": [...]}
        customers_list = data['customers']
        print(f"[OK] Loaded {len(customers_list)} existing customers (list format)")
    elif isinstance(data, list):
        # Old format: [...]
        customers_list = data
        print(f"[OK] Loaded {len(customers_list)} existing customers (array format)")
    else:
        print(f"[ERROR] Unknown format: {type(data)}")
        exit(1)

except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"[WARN] customers.json not found or invalid: {e}")
    customers_list = []

# Check if customer already exists
existing = None
for i, c in enumerate(customers_list):
    if c.get('customer_id') == 'qdrant_main' or c.get('collection_name') == 'qdrant_customer_embedding':
        existing = i
        break

if existing is not None:
    print(f"[*] Customer already exists at index {existing}, updating...")
    customers_list[existing] = customer_data
else:
    print(f"[*] Adding new customer...")
    customers_list.append(customer_data)

# Save back in the same format
if isinstance(data, dict) and 'customers' in data:
    data['customers'] = customers_list
    save_data = data
else:
    save_data = {"customers": customers_list}

with open(customers_file, 'w', encoding='utf-8') as f:
    json.dump(save_data, f, indent=2, ensure_ascii=False)

print(f"[OK] Customer saved to {customers_file}")
print(f"[INFO] Total customers: {len(customers_list)}")
print(f"[INFO] Customer ID: {customer_data['customer_id']}")
print(f"[INFO] Collection: {customer_data['collection_name']}")
print(f"\n[SUCCESS] Customer entry created!")
