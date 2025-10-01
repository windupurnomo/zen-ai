"""
FastAPI Application for NL2SQL Service
REST API untuk mengubah Natural Language (Bahasa Indonesia) menjadi SQL Query
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from schemas import NL2SQLRequest, NL2SQLResponse, HealthResponse
from service import NL2SQLService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NL2SQL API",
    description="API untuk mengubah Natural Language (Bahasa Indonesia) menjadi SQL Query untuk tabel todo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service (singleton)
nl2sql_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize NL2SQL service on startup"""
    global nl2sql_service
    logger.info("Starting NL2SQL API...")
    try:
        nl2sql_service = NL2SQLService()
        logger.info("NL2SQL service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NL2SQL service: {str(e)}")
        raise


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse: Status kesehatan service
    """
    return HealthResponse(
        status="healthy",
        service="NL2SQL API",
        version="1.0.0"
    )


@app.post("/api/v1/nl2sql", response_model=NL2SQLResponse, tags=["NL2SQL"])
async def convert_nl_to_sql(request: NL2SQLRequest):
    """
    Convert Natural Language (Bahasa Indonesia) ke SQL Query

    Endpoint ini menerima kalimat dalam bahasa Indonesia dan mengubahnya
    menjadi SQL query untuk tabel todo.

    **Supported Intents:**
    - `show_all`: Menampilkan semua task
    - `show_done`: Menampilkan task yang sudah selesai
    - `show_pending`: Menampilkan task yang belum selesai
    - `insert_task`: Menambah task baru
    - `delete_task`: Menghapus task berdasarkan ID
    - `update_status`: Mengubah status task

    **Contoh Input:**
    - "Tampilkan semua task"
    - "Buat task belajar Python"
    - "Hapus task nomor 3"
    - "Update status task 2 jadi done"

    Args:
        request: NL2SQLRequest dengan message input

    Returns:
        NL2SQLResponse: Response berisi intent, confidence, dan SQL query

    Raises:
        HTTPException: Jika terjadi error internal
    """
    try:
        logger.info(f"Processing request: {request.message}")

        # Process input
        result = nl2sql_service.process(request.message)

        logger.info(
            f"Result - Intent: {result['intent']}, "
            f"Confidence: {result['confidence']}, "
            f"Success: {result['success']}"
        )

        return NL2SQLResponse(**result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/v1/intents", tags=["Info"])
async def get_supported_intents():
    """
    Get list of supported intents

    Returns:
        dict: Dictionary berisi list intent yang didukung beserta deskripsinya
    """
    try:
        intents = nl2sql_service.get_supported_intents()

        intent_descriptions = {
            "show_all": "Menampilkan semua task",
            "show_done": "Menampilkan task yang sudah selesai",
            "show_pending": "Menampilkan task yang belum selesai",
            "insert_task": "Menambah task baru",
            "delete_task": "Menghapus task berdasarkan ID",
            "update_status": "Mengubah status task"
        }

        return {
            "intents": [
                {
                    "name": intent,
                    "description": intent_descriptions.get(intent, "No description")
                }
                for intent in intents
            ],
            "total": len(intents)
        }

    except Exception as e:
        logger.error(f"Error getting intents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found. Visit /docs untuk API documentation."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
