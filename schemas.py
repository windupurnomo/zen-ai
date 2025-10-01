"""
Pydantic schemas for API request and response models
"""

from typing import Optional
from pydantic import BaseModel, Field


class NL2SQLRequest(BaseModel):
    """Request model untuk NL2SQL endpoint"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Natural language input dalam bahasa Indonesia",
        examples=["buat task belajar Python"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "buat task belajar Python"
            }
        }


class NL2SQLResponse(BaseModel):
    """Response model untuk NL2SQL endpoint"""
    success: bool = Field(
        ...,
        description="Status keberhasilan proses"
    )
    intent: Optional[str] = Field(
        None,
        description="Intent yang terdeteksi (show_all, insert_task, delete_task, update_status, show_done, show_pending)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score dari intent classification (0.0 - 1.0)"
    )
    sql_query: Optional[str] = Field(
        None,
        description="SQL query yang di-generate"
    )
    input: str = Field(
        ...,
        description="Input original dari user"
    )
    error: Optional[str] = Field(
        None,
        description="Error message jika ada"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "intent": "insert_task",
                    "confidence": 0.856,
                    "sql_query": "INSERT INTO todo (task, status) VALUES ('belajar python', 'pending');",
                    "input": "buat task belajar Python",
                    "error": None
                },
                {
                    "success": False,
                    "intent": None,
                    "confidence": 0.432,
                    "sql_query": None,
                    "input": "kalimat tidak jelas",
                    "error": "Intent tidak dapat diidentifikasi"
                }
            ]
        }


class HealthResponse(BaseModel):
    """Response model untuk health check endpoint"""
    status: str = Field(
        ...,
        description="Health status"
    )
    service: str = Field(
        ...,
        description="Service name"
    )
    version: str = Field(
        ...,
        description="API version"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "NL2SQL API",
                "version": "1.0.0"
            }
        }
