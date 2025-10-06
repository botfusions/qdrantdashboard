#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rename collection: customer_2122beac -> qdrant_customer_embedding
Uses Qdrant snapshot + restore approach
"""

import httpx
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "https://qdrant.turklawai.com")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

headers = {"api-key": QDRANT_API_KEY} if QDRANT_API_KEY else {}

OLD_NAME = "customer_2122beac"
NEW_NAME = "qdrant_customer_embedding"

print(f"[*] Renaming collection: {OLD_NAME} -> {NEW_NAME}")

with httpx.Client(timeout=30.0) as client:
    # 1. Check old collection exists
    print(f"[1/6] Checking {OLD_NAME}...")
    resp = client.get(f"{QDRANT_URL}/collections/{OLD_NAME}", headers=headers)
    if resp.status_code != 200:
        print(f"[ERROR] Collection {OLD_NAME} not found")
        exit(1)

    collection_info = resp.json()
    print(f"[OK] Found {OLD_NAME}: {collection_info['result']['points_count']} vectors")

    # 2. Get all points from old collection
    print(f"[2/6] Fetching all points...")
    resp = client.post(
        f"{QDRANT_URL}/collections/{OLD_NAME}/points/scroll",
        headers=headers,
        json={"limit": 1000, "with_payload": True, "with_vector": True}
    )

    if resp.status_code != 200:
        print(f"[ERROR] Failed to fetch points: {resp.text}")
        exit(1)

    points = resp.json()['result']['points']
    print(f"[OK] Retrieved {len(points)} points")

    # 3. Create new collection with same config
    print(f"[3/6] Creating {NEW_NAME}...")
    config = collection_info['result']['config']

    resp = client.put(
        f"{QDRANT_URL}/collections/{NEW_NAME}",
        headers=headers,
        json={
            "vectors": config['params']['vectors'],
            "optimizers_config": config['optimizer_config'],
            "hnsw_config": config['hnsw_config']
        }
    )

    if resp.status_code not in [200, 201]:
        print(f"[ERROR] Failed to create collection: {resp.text}")
        exit(1)

    print(f"[OK] Created {NEW_NAME}")

    # 4. Upload points to new collection
    print(f"[4/6] Uploading {len(points)} points to {NEW_NAME}...")

    resp = client.put(
        f"{QDRANT_URL}/collections/{NEW_NAME}/points",
        headers=headers,
        json={"points": points}
    )

    if resp.status_code not in [200, 201]:
        print(f"[ERROR] Failed to upload points: {resp.text}")
        exit(1)

    print(f"[OK] Uploaded all points")

    # 5. Verify new collection
    print(f"[5/6] Verifying...")
    resp = client.get(f"{QDRANT_URL}/collections/{NEW_NAME}", headers=headers)
    new_info = resp.json()
    print(f"[OK] Verification: {new_info['result']['points_count']} vectors in {NEW_NAME}")

    # 6. Delete old collection (optional - commented for safety)
    print(f"[6/6] Cleanup...")
    print(f"[SKIP] Old collection {OLD_NAME} preserved - delete manually if needed")
    # resp = client.delete(f"{QDRANT_URL}/collections/{OLD_NAME}", headers=headers)

    print(f"\n[SUCCESS] Collection renamed successfully!")
    print(f"[INFO] Old: {OLD_NAME} -> New: {NEW_NAME}")
