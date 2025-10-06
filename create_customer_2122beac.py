#!/usr/bin/env python3
"""
Script to create customer_2122beac in customers.json
Run once to restore customer data
"""

import json
from datetime import datetime
from pathlib import Path

# Customer data
customer_data = {
    "customer_2122beac": {
        "customer_id": "customer_2122beac",
        "name": "Customer 2122beac",
        "collection_name": "customer_2122beac",
        "quota_mb": 1000,
        "used_mb": 0,  # Will be calculated from Qdrant
        "document_count": 2,
        "created_at": "2025-10-01T00:00:00",
        "updated_at": datetime.utcnow().isoformat()
    }
}

# Path to customers.json
customers_file = Path(__file__).parent / "customers.json"

# Read existing customers
try:
    with open(customers_file, 'r', encoding='utf-8') as f:
        customers = json.load(f)
    print(f"✅ Loaded existing customers: {list(customers.keys())}")
except (FileNotFoundError, json.JSONDecodeError):
    customers = {}
    print("⚠️  No existing customers.json found, creating new")

# Add/update customer_2122beac
customers.update(customer_data)

# Save
with open(customers_file, 'w', encoding='utf-8') as f:
    json.dump(customers, f, indent=2, ensure_ascii=False)

print(f"✅ Customer saved to {customers_file}")
print(f"📊 Total customers: {len(customers)}")
print(f"👤 Customers: {list(customers.keys())}")
