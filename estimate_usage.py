"""
Estimate customer usage from Qdrant text chunks
Calculates approximate MB usage based on text length
"""
import json
import httpx

CUSTOMER_ID = "2122beac"
COLLECTION_NAME = "customer_2122beac"

QDRANT_URL = "https://qdrant.turklawai.com"
API_KEY = "PVrZ8QZkHrn4MFCvlZRhor1DMuoDr5l6"
headers = {"api-key": API_KEY}

print(f"[*] Fetching points from {COLLECTION_NAME}...")

# Fetch all points with scroll
all_points = []
offset = None

while True:
    payload = {
        "limit": 100,
        "with_payload": True,
        "with_vector": False
    }

    if offset:
        payload["offset"] = offset

    response = httpx.post(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll",
        headers=headers,
        json=payload,
        timeout=30.0
    )

    result = response.json()["result"]
    points = result["points"]
    all_points.extend(points)

    print(f"    Fetched {len(points)} points (total: {len(all_points)})")

    # Check if there are more points
    offset = result.get("next_page_offset")
    if not offset or len(points) == 0:
        break

print(f"\n[+] Total points fetched: {len(all_points)}")

# Calculate estimated size
total_bytes = 0
unique_docs = {}

for point in all_points:
    payload = point.get("payload", {})
    text = payload.get("text", "")

    # Estimate bytes (UTF-8 encoding)
    # Each character is typically 1-3 bytes in UTF-8
    # Turkish characters (ç, ğ, ı, ş, ü, ö) are 2 bytes
    # We'll use a conservative estimate: 1.5 bytes per character average
    text_bytes = len(text.encode('utf-8'))
    total_bytes += text_bytes

    # Track unique documents
    doc_id = payload.get("document_id", payload.get("filename", f"doc_{point['id']}"))
    if doc_id not in unique_docs:
        unique_docs[doc_id] = 0
    unique_docs[doc_id] += text_bytes

# Convert to MB
total_mb = total_bytes / (1024 * 1024)

print(f"\n[*] Usage Statistics:")
print(f"    Total chunks: {len(all_points)}")
print(f"    Unique documents: {len(unique_docs)}")
print(f"    Total bytes: {total_bytes:,}")
print(f"    Estimated MB: {total_mb:.2f}")

# Document breakdown
print(f"\n[*] Document Breakdown:")
for doc_id, doc_bytes in sorted(unique_docs.items(), key=lambda x: x[1], reverse=True):
    doc_mb = doc_bytes / (1024 * 1024)
    print(f"    {doc_id}: {doc_mb:.3f} MB ({doc_bytes:,} bytes)")

# Update customers.json
print(f"\n[*] Updating customers.json...")

with open("customers.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for customer in data["customers"]:
    if customer["customer_id"] == CUSTOMER_ID:
        customer["document_count"] = len(unique_docs)
        customer["used_mb"] = round(total_mb, 2)
        customer["usage_percent"] = round((total_mb / customer["quota_mb"]) * 100, 1)
        customer["remaining_mb"] = round(customer["quota_mb"] - total_mb, 2)

        print(f"\n[+] Updated customer: {customer['name']}")
        print(f"    Document count: {customer['document_count']}")
        print(f"    Used MB: {customer['used_mb']:.2f}")
        print(f"    Usage: {customer['usage_percent']}%")
        print(f"    Remaining: {customer['remaining_mb']:.2f} MB")

with open("customers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n[✓] customers.json updated successfully!")
