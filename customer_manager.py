"""
Customer Management Module
Multi-tenant customer tracking with quota management
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

CUSTOMERS_FILE = Path(__file__).parent / "customers.json"


class Customer:
    """Customer model with quota tracking"""

    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        quota_mb: int = 100,
        used_mb: float = 0.0,
        collection_name: str = None,
        created_at: str = None,
        active: bool = True
    ):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.quota_mb = quota_mb
        self.used_mb = used_mb
        self.collection_name = collection_name or f"customer_{customer_id}"
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.active = active
        self.document_count = 0
        self.last_upload = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "quota_mb": self.quota_mb,
            "used_mb": round(self.used_mb, 2),
            "collection_name": self.collection_name,
            "created_at": self.created_at,
            "active": self.active,
            "document_count": self.document_count,
            "last_upload": self.last_upload,
            "usage_percent": round((self.used_mb / self.quota_mb) * 100, 1) if self.quota_mb > 0 else 0,
            "remaining_mb": round(self.quota_mb - self.used_mb, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Customer':
        """Create from dictionary"""
        customer = cls(
            customer_id=data['customer_id'],
            name=data['name'],
            email=data['email'],
            quota_mb=data.get('quota_mb', 100),
            used_mb=data.get('used_mb', 0.0),
            collection_name=data.get('collection_name'),
            created_at=data.get('created_at'),
            active=data.get('active', True)
        )
        customer.document_count = data.get('document_count', 0)
        customer.last_upload = data.get('last_upload')
        return customer


class CustomerManager:
    """Manage customers and their quotas"""

    def __init__(self):
        self.customers_file = CUSTOMERS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create customers file if not exists"""
        if not self.customers_file.exists():
            self._save_data({"customers": []})

    def _load_data(self) -> Dict:
        """Load customers from JSON"""
        try:
            with open(self.customers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading customers: {e}")
            return {"customers": []}

    def _save_data(self, data: Dict):
        """Save customers to JSON"""
        with open(self.customers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_customer(
        self,
        name: str,
        email: str,
        quota_mb: int = 100
    ) -> Customer:
        """Create new customer"""
        customer_id = str(uuid.uuid4())[:8]
        customer = Customer(
            customer_id=customer_id,
            name=name,
            email=email,
            quota_mb=quota_mb
        )

        data = self._load_data()
        data['customers'].append(customer.to_dict())
        self._save_data(data)

        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        data = self._load_data()
        for c in data['customers']:
            if c['customer_id'] == customer_id:
                return Customer.from_dict(c)
        return None

    def get_all_customers(self) -> List[Customer]:
        """Get all customers"""
        data = self._load_data()
        return [Customer.from_dict(c) for c in data['customers']]

    def update_customer(self, customer_id: str, updates: Dict) -> bool:
        """Update customer data"""
        data = self._load_data()
        for i, c in enumerate(data['customers']):
            if c['customer_id'] == customer_id:
                data['customers'][i].update(updates)
                self._save_data(data)
                return True
        return False

    def delete_customer(self, customer_id: str) -> bool:
        """Delete customer"""
        data = self._load_data()
        original_len = len(data['customers'])
        data['customers'] = [c for c in data['customers'] if c['customer_id'] != customer_id]

        if len(data['customers']) < original_len:
            self._save_data(data)
            return True
        return False

    def add_usage(self, customer_id: str, mb: float) -> bool:
        """Add usage to customer quota"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False

        new_used = customer.used_mb + mb
        if new_used > customer.quota_mb:
            return False  # Quota exceeded

        return self.update_customer(customer_id, {
            "used_mb": round(new_used, 2),
            "last_upload": datetime.utcnow().isoformat()
        })

    def increment_document_count(self, customer_id: str) -> bool:
        """Increment document count"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False

        return self.update_customer(customer_id, {
            "document_count": customer.document_count + 1,
            "last_upload": datetime.utcnow().isoformat()
        })

    def get_stats(self) -> Dict:
        """Get overall statistics"""
        customers = self.get_all_customers()

        total_customers = len(customers)
        active_customers = len([c for c in customers if c.active])
        total_quota = sum(c.quota_mb for c in customers)
        total_used = sum(c.used_mb for c in customers)
        total_documents = sum(c.document_count for c in customers)

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "total_quota_mb": total_quota,
            "total_used_mb": round(total_used, 2),
            "total_documents": total_documents,
            "avg_usage_percent": round((total_used / total_quota * 100) if total_quota > 0 else 0, 1)
        }
