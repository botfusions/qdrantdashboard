"""
Qdrant Dashboard Backend API
FastAPI-based dashboard for managing Qdrant vector database
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
import tempfile
import uuid
from pathlib import Path
from customer_manager import CustomerManager, Customer
from embedding_service import get_embedding_service
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    change_user_password
)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "https://qdrant.turklawai.com")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "PVrZ8QZkHrn4MFCvlZRhor1DMuoDr5l6")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")  # n8n embedding webhook
PORT = int(os.getenv("PORT", 8081))

# Initialize services
customer_manager = CustomerManager()
embedding_service = None  # Lazy load
qdrant_client = None  # Lazy load

def get_qdrant_client():
    """Get or create Qdrant client"""
    global qdrant_client
    if qdrant_client is None:
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY if QDRANT_API_KEY else None)
    return qdrant_client

app = FastAPI(
    title="Qdrant Dashboard API",
    description="Management dashboard for Qdrant vector database with multi-tenant support",
    version="2.0.0"
)

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CustomerCreate(BaseModel):
    name: str
    email: str
    quota_mb: int = 100

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    quota_mb: Optional[int] = None
    active: Optional[bool] = None

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# Helper function for Qdrant API calls
async def qdrant_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make authenticated requests to Qdrant API"""
    headers = {}
    if QDRANT_API_KEY:
        headers["api-key"] = QDRANT_API_KEY

    url = f"{QDRANT_URL}/{endpoint.lstrip('/')}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Qdrant API error: {str(e)}")


# Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard HTML"""
    html_file = BASE_DIR / "templates" / "index.html"
    return FileResponse(html_file)


@app.get("/simple", response_class=HTMLResponse)
async def simple_collections():
    """Simple collections page"""
    html_file = BASE_DIR / "templates" / "simple.html"
    return FileResponse(html_file)


@app.get("/api/health")
async def health_check():
    """Check dashboard API health"""
    return {
        "status": "healthy",
        "qdrant_url": QDRANT_URL
    }


@app.get("/api/debug/users")
async def debug_users():
    """Debug endpoint to check users.json"""
    from auth import get_users
    import json
    from pathlib import Path

    users_file = Path(__file__).parent / "users.json"

    try:
        # Check if file exists
        if not users_file.exists():
            return {"error": "users.json not found", "path": str(users_file)}

        # Read raw content
        with open(users_file, 'r') as f:
            raw_content = f.read()

        # Try to parse
        try:
            users = get_users()
            return {
                "status": "ok",
                "users_count": len(users),
                "usernames": list(users.keys()),
                "raw_content_preview": raw_content[:200]
            }
        except Exception as e:
            return {
                "error": "Failed to parse users",
                "exception": str(e),
                "raw_content": raw_content
            }
    except Exception as e:
        return {"error": str(e)}


# ============================================
# Authentication Endpoints
# ============================================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT token
    Default credentials: admin / admin123
    """
    try:
        user = authenticate_user(login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )

        # Create access token
        access_token = create_access_token(data={"sub": user["username"]})

        return TokenResponse(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[!] Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint (client-side token removal)
    """
    return {"message": "Logged out successfully"}


@app.post("/api/auth/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change current user's password"""
    username = current_user["username"]

    success = change_user_password(
        username,
        password_data.old_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Incorrect old password"
        )

    return {"message": "Password changed successfully"}


@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "username": current_user["username"],
        "role": current_user.get("role", "user")
    }


@app.get("/api/qdrant/status")
async def qdrant_status():
    """Get Qdrant instance status"""
    try:
        result = await qdrant_request("/")
        return {
            "status": "online",
            "data": result
        }
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e)
        }


@app.get("/api/qdrant/collections")
async def get_collections():
    """Get all collections from Qdrant"""
    try:
        result = await qdrant_request("/collections")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qdrant/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get specific collection information"""
    try:
        result = await qdrant_request(f"/collections/{collection_name}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qdrant/collections/{collection_name}")
async def create_collection(collection_name: str, config: dict):
    """Create a new collection"""
    try:
        result = await qdrant_request(
            f"/collections/{collection_name}",
            method="PUT",
            data=config
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/qdrant/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        result = await qdrant_request(
            f"/collections/{collection_name}",
            method="DELETE"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qdrant/cluster")
async def get_cluster_info():
    """Get cluster information"""
    try:
        result = await qdrant_request("/cluster")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qdrant/telemetry")
async def get_telemetry():
    """Get Qdrant telemetry data"""
    try:
        result = await qdrant_request("/telemetry")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qdrant/metrics")
async def get_metrics():
    """Get Qdrant Prometheus metrics"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{QDRANT_URL}/metrics")
            response.raise_for_status()
            return {"metrics": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qdrant/collections/{collection_name}/points/search")
async def search_points(collection_name: str, search_data: dict):
    """Search points in a collection"""
    try:
        result = await qdrant_request(
            f"/collections/{collection_name}/points/search",
            method="POST",
            data=search_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Customer Management Endpoints
# ============================================

@app.get("/api/customers")
async def get_all_customers():
    """Get all customers"""
    customers = customer_manager.get_all_customers()
    return {
        "customers": [c.to_dict() for c in customers],
        "total": len(customers)
    }


@app.get("/api/customers/stats")
async def get_customer_stats():
    """Get customer statistics"""
    return customer_manager.get_stats()


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get specific customer"""
    customer = customer_manager.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.to_dict()


@app.post("/api/customers")
async def create_customer(customer_data: CustomerCreate):
    """Create new customer"""
    try:
        customer = customer_manager.create_customer(
            name=customer_data.name,
            email=customer_data.email,
            quota_mb=customer_data.quota_mb
        )

        # Create collection for customer in Qdrant
        collection_config = {
            "vectors": {
                "size": 1536,  # Default OpenAI embedding size
                "distance": "Cosine"
            }
        }

        try:
            await qdrant_request(
                f"/collections/{customer.collection_name}",
                method="PUT",
                data=collection_config
            )
        except Exception as e:
            print(f"Warning: Could not create Qdrant collection: {e}")

        return {
            "success": True,
            "customer": customer.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/customers/{customer_id}")
async def update_customer(customer_id: str, updates: CustomerUpdate):
    """Update customer"""
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}

    success = customer_manager.update_customer(customer_id, update_dict)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer = customer_manager.get_customer(customer_id)
    return {
        "success": True,
        "customer": customer.to_dict()
    }


@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete customer and their collection"""
    customer = customer_manager.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Delete Qdrant collection
    try:
        await qdrant_request(
            f"/collections/{customer.collection_name}",
            method="DELETE"
        )
    except Exception as e:
        print(f"Warning: Could not delete Qdrant collection: {e}")

    # Delete customer record
    success = customer_manager.delete_customer(customer_id)

    return {
        "success": success,
        "message": f"Customer {customer_id} deleted"
    }


@app.post("/api/customers/{customer_id}/upload")
async def upload_document(
    customer_id: str,
    file: UploadFile = File(...),
    description: str = Form(None)
):
    """
    Upload document for customer with n8n embedding workflow

    Process:
    1. Validate customer and quota
    2. Send file to n8n webhook for processing
    3. n8n returns embeddings
    4. Write embeddings to Qdrant
    5. Update customer usage
    """
    customer = customer_manager.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Read file
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    # Check quota
    if customer.used_mb + file_size_mb > customer.quota_mb:
        raise HTTPException(
            status_code=400,
            detail=f"Quota exceeded. Used: {customer.used_mb}MB, Limit: {customer.quota_mb}MB"
        )

    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.txt', '.doc', '.docx']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, TXT, DOC, or DOCX")

    # Check n8n webhook configured
    if not N8N_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_WEBHOOK_URL not configured")

    try:
        print(f"[*] Sending document to n8n webhook: {file.filename}")

        # Send to n8n webhook
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Prepare multipart form data
            files = {
                'file': (file.filename, content, file.content_type)
            }
            data = {
                'customer_id': customer_id,
                'customer_name': customer.name,
                'customer_email': customer.email,
                'description': description or '',
                'collection_name': customer.collection_name
            }

            response = await client.post(
                N8N_WEBHOOK_URL,
                files=files,
                data=data
            )
            response.raise_for_status()
            n8n_result = response.json()

        print(f"[*] n8n processing complete")

        # n8n returns embeddings in format: [{ id, text, embedding, metadata }]
        embeddings_data = n8n_result.get('embeddings', [])

        if not embeddings_data:
            raise HTTPException(status_code=500, detail="No embeddings returned from n8n")

        # Upload to Qdrant
        client = get_qdrant_client()

        points = []
        for item in embeddings_data:
            points.append(
                PointStruct(
                    id=item['id'],
                    vector=item['embedding'],
                    payload={
                        "customer_id": customer_id,
                        "filename": file.filename,
                        "text": item['text'],
                        "kind": item.get('kind', 'document'),
                        "question": item.get('question'),
                        "answer": item.get('answer'),
                        "chunk_index": item.get('chunk_index', 0),
                        "chunk_total": item.get('chunk_total', 1),
                        "description": description or "",
                        "file_size_mb": file_size_mb,
                        "metadata": item.get('metadata', {})
                    }
                )
            )

        # Upload to Qdrant collection
        client.upsert(
            collection_name=customer.collection_name,
            points=points
        )

        # Update usage
        customer_manager.add_usage(customer_id, file_size_mb)
        customer_manager.increment_document_count(customer_id)

        print(f"[*] Document uploaded successfully: {len(points)} chunks")

        return {
            "success": True,
            "message": "Document uploaded and embedded successfully",
            "file_name": file.filename,
            "size_mb": round(file_size_mb, 2),
            "chunks_created": len(points),
            "embedding_model": embeddings_data[0].get('embedding_model', 'unknown'),
            "embedding_dim": embeddings_data[0].get('embedding_dim', 1536),
            "customer": customer_manager.get_customer(customer_id).to_dict()
        }

    except httpx.HTTPError as e:
        print(f"[!] n8n webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"n8n processing failed: {str(e)}")
    except Exception as e:
        print(f"[!] Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/customers/{customer_id}/documents")
async def get_customer_documents(customer_id: str):
    """Get list of documents for a customer from their Qdrant collection"""
    customer = customer_manager.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        client = get_qdrant_client()

        # Scroll through collection to get unique documents
        scroll_result = client.scroll(
            collection_name=customer.collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )

        # Group by filename
        documents = {}
        for point in scroll_result[0]:
            filename = point.payload.get("filename", "unknown")
            if filename not in documents:
                documents[filename] = {
                    "filename": filename,
                    "chunks": 0,
                    "description": point.payload.get("description", ""),
                    "file_size_mb": point.payload.get("file_size_mb", 0)
                }
            documents[filename]["chunks"] += 1

        return {
            "customer_id": customer_id,
            "collection_name": customer.collection_name,
            "documents": list(documents.values()),
            "total_documents": len(documents),
            "total_chunks": len(scroll_result[0])
        }

    except Exception as e:
        return {
            "customer_id": customer_id,
            "collection_name": customer.collection_name,
            "documents": [],
            "total_documents": 0,
            "total_chunks": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    print(f"[*] Qdrant Dashboard starting on http://0.0.0.0:{PORT}")
    print(f"[*] Qdrant URL: {QDRANT_URL}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
