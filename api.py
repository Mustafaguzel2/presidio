#!/usr/bin/env python3
"""
Presidio PII Analyzer - FastAPI Application
High-performance API with singleton pattern for shared analyzer engines
"""

import os
import tempfile
import shutil
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

from analyzers.optimized_pdf_analyzer import OptimizedPDFAnalyzer
from analyzers.optimized_image_analyzer import OptimizedImageAnalyzer
from analyzers.optimized_csv_analyzer import OptimizedCSVAnalyzer
from analyzers.singleton_analyzers import get_analyzer_singleton
from maskers.pdf_masker import PDFMasker
from maskers.image_masker import ImageMasker


# Pydantic models for API documentation
class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., description="Text to analyze for PII")
    threshold: float = Field(0.35, ge=0.0, le=1.0, description="Minimum confidence score")
    entities: Optional[List[str]] = Field(None, description="List of entity types to detect (None = all)")


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    pii_found: bool
    pii_count: int
    pii_findings: List[dict]
    entities_filter: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    analyzer_loaded: bool
    supported_entities: List[str]


# Initialize FastAPI app
app = FastAPI(
    title="Presidio PII Analyzer API",
    description="High-performance PII detection and anonymization API using Microsoft Presidio",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global analyzers (initialized once at startup)
pdf_analyzer: OptimizedPDFAnalyzer = None
image_analyzer: OptimizedImageAnalyzer = None
csv_analyzer: OptimizedCSVAnalyzer = None
pdf_masker: PDFMasker = None
image_masker: ImageMasker = None
singleton = None

# Downloaded files directory - all masked files are saved here
DOWNLOAD_FOLDER = "downloaded"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """
    Initialize analyzers on app startup (one-time operation).
    This loads the Spacy NER model and Presidio engines once.
    """
    global pdf_analyzer, image_analyzer, csv_analyzer, pdf_masker, image_masker, singleton
    
    print("\n" + "="*70)
    print("🚀 Starting Presidio PII Analyzer API")
    print("="*70)
    
    # Initialize singleton (loads Presidio engines and Spacy model)
    singleton = get_analyzer_singleton()
    
    # Initialize optimized analyzers (they use the singleton)
    print("📦 Initializing analyzers...")
    pdf_analyzer = OptimizedPDFAnalyzer()
    image_analyzer = OptimizedImageAnalyzer()
    csv_analyzer = OptimizedCSVAnalyzer()
    
    # Initialize maskers
    pdf_masker = PDFMasker()
    image_masker = ImageMasker()
    
    print("✅ All analyzers ready!")
    print(f"📋 Supported entities: {len(singleton.get_supported_entities())}")
    print("="*70)
    print("🌐 API is ready to accept requests!")
    print("📖 Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Presidio PII Analyzer API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "text_analysis": "/api/analyze/text",
            "pdf_analysis": "/api/analyze/pdf",
            "image_analysis": "/api/analyze/image",
            "csv_analysis": "/api/analyze/csv",
            "entities": "/api/entities"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        supported = singleton.get_supported_entities() if singleton else []
        return HealthResponse(
            status="healthy",
            analyzer_loaded=singleton is not None,
            supported_entities=supported
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/api/entities", response_model=dict)
async def get_supported_entities():
    """Get list of all supported entity types"""
    try:
        entities = singleton.get_supported_entities()
        return {
            "total": len(entities),
            "entities": sorted(entities),
            "common_entities": [
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
                "US_SSN", "LOCATION", "DATE_TIME", "IP_ADDRESS", "URL"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/text", response_model=AnalysisResponse)
async def analyze_text(
    text: str = Form(..., description="Text to analyze"),
    threshold: float = Form(0.35, ge=0.0, le=1.0, description="Confidence threshold"),
    entities: Optional[str] = Form(None, description="Comma-separated entity types (e.g., PERSON,EMAIL_ADDRESS)")
):
    """
    Analyze plain text for PII
    
    - **text**: Text content to analyze
    - **threshold**: Minimum confidence score (0.0-1.0)
    - **entities**: Optional comma-separated list of entity types
    """
    try:
        # Parse entities
        entity_list = entities.split(",") if entities else None
        if entity_list:
            entity_list = [e.strip().upper() for e in entity_list if e.strip()]
        
        # Analyze using shared engine
        pii_findings = pdf_analyzer.analyze_text(
            text=text,
            threshold=threshold,
            entities=entity_list
        )
        
        return AnalysisResponse(
            pii_found=len(pii_findings) > 0,
            pii_count=len(pii_findings),
            pii_findings=pii_findings,
            entities_filter=",".join(entity_list) if entity_list else "all"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/pdf")
async def analyze_pdf(
    file: UploadFile = File(..., description="PDF file to analyze"),
    threshold: float = Form(0.35, ge=0.0, le=1.0),
    entities: Optional[str] = Form(None, description="Comma-separated entity types"),
    anonymize: bool = Form(False, description="Generate anonymized version")
):
    """
    Analyze PDF file for PII
    
    - **file**: PDF file upload
    - **threshold**: Minimum confidence score
    - **entities**: Optional entity filter
    - **anonymize**: Whether to create masked version (returns file directly if true)
    
    **Returns**: JSON with analysis if anonymize=false, or masked PDF file if anonymize=true
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create temp file
    temp_dir = tempfile.mkdtemp()
    temp_input = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse entities
        entity_list = entities.split(",") if entities else None
        if entity_list:
            entity_list = [e.strip().upper() for e in entity_list if e.strip()]
        
        # Analyze
        results = pdf_analyzer.analyze_pdf(
            pdf_path=temp_input,
            anonymize=anonymize,
            threshold=threshold,
            entities=entity_list
        )
        
        # Add metadata
        results['file_type'] = 'pdf'
        results['entities_filter'] = entity_list if entity_list else 'all'
        
        # If anonymize, create masked PDF and include download URL in response
        if anonymize and results.get('pii_found'):
            # Create better filename: document.pdf → document_masked.pdf
            file_base, file_ext = os.path.splitext(file.filename)
            masked_filename = f"{file_base}_masked{file_ext}"
            
            # Save to downloaded folder
            download_path = os.path.join(DOWNLOAD_FOLDER, masked_filename)
            
            anonymized_text = results.get('anonymized_text', '')
            pdf_masker.create_masked_pdf(temp_input, anonymized_text, download_path)
            
            # Add download info to results
            results['masked_file'] = masked_filename
            results['download_url'] = f"/api/download/{masked_filename}"
            results['download_path'] = download_path
        
        # Remove large text fields for response
        if 'original_text' in results and len(results['original_text']) > 500:
            results['original_text'] = f"<{len(results['original_text'])} characters>"
        
        return JSONResponse(content=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Note: In production, implement proper cleanup with background tasks
        pass


@app.post("/api/analyze/image")
async def analyze_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    threshold: float = Form(0.35, ge=0.0, le=1.0),
    entities: Optional[str] = Form(None),
    anonymize: bool = Form(False)
):
    """
    Analyze image file for PII using OCR
    
    - **file**: Image file (PNG, JPG, etc.)
    - **threshold**: Minimum confidence score
    - **entities**: Optional entity filter
    - **anonymize**: Whether to create masked version (returns file directly if true)
    
    **Returns**: JSON with analysis if anonymize=false, or masked image file if anonymize=true
    """
    # Validate file type
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported image format. Allowed: {allowed_extensions}")
    
    temp_dir = tempfile.mkdtemp()
    temp_input = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse entities
        entity_list = entities.split(",") if entities else None
        if entity_list:
            entity_list = [e.strip().upper() for e in entity_list if e.strip()]
        
        # Analyze
        results = image_analyzer.analyze_image(
            image_path=temp_input,
            anonymize=anonymize,
            threshold=threshold,
            entities=entity_list
        )
        
        # Add metadata
        results['file_type'] = 'image'
        results['entities_filter'] = entity_list if entity_list else 'all'
        
        # If anonymize, create masked image and include download URL in response
        if anonymize and results.get('pii_found'):
            # Create better filename: screenshot.png → screenshot_masked.png
            file_base, _ = os.path.splitext(file.filename)
            masked_filename = f"{file_base}_masked{file_ext}"
            
            # Save to downloaded folder
            download_path = os.path.join(DOWNLOAD_FOLDER, masked_filename)
            
            image_masker.create_masked_image(temp_input, results['pii_findings'], download_path)
            
            # Add download info to results
            results['masked_file'] = masked_filename
            results['download_url'] = f"/api/download/{masked_filename}"
            results['download_path'] = download_path
        
        return JSONResponse(content=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass


@app.post("/api/analyze/csv")
async def analyze_csv(
    file: UploadFile = File(..., description="CSV file to analyze"),
    threshold: float = Form(0.35, ge=0.0, le=1.0),
    entities: Optional[str] = Form(None),
    sample_size: Optional[int] = Form(None, description="Sample size for large CSVs"),
    anonymize: bool = Form(False)
):
    """
    Analyze CSV file for PII
    
    - **file**: CSV file upload
    - **threshold**: Minimum confidence score
    - **entities**: Optional entity filter
    - **sample_size**: Number of rows to sample (for large files)
    - **anonymize**: Whether to create masked version (returns file directly if true)
    
    **Returns**: JSON with analysis if anonymize=false, or masked CSV file if anonymize=true
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    temp_dir = tempfile.mkdtemp()
    temp_input = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse entities
        entity_list = entities.split(",") if entities else None
        if entity_list:
            entity_list = [e.strip().upper() for e in entity_list if e.strip()]
        
        # Prepare output path if anonymizing
        # Create better filename: data.csv → data_masked.csv
        if anonymize:
            file_base, file_ext = os.path.splitext(file.filename)
            masked_filename = f"{file_base}_masked{file_ext}"
            # Save to downloaded folder
            temp_output = os.path.join(DOWNLOAD_FOLDER, masked_filename)
        else:
            temp_output = None
            masked_filename = None
        
        # Analyze
        results = csv_analyzer.analyze_csv(
            csv_path=temp_input,
            anonymize=anonymize,
            output_path=temp_output,
            sample_size=sample_size,
            threshold=threshold,
            entities=entity_list
        )
        
        # Add metadata
        results['file_type'] = 'csv'
        results['entities_filter'] = entity_list if entity_list else 'all'
        
        # If anonymize, include download URL in response
        if anonymize and temp_output and os.path.exists(temp_output):
            # Add download info to results
            results['masked_file'] = masked_filename
            results['download_url'] = f"/api/download/{masked_filename}"
            results['download_path'] = temp_output
        
        return JSONResponse(content=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download anonymized file
    
    After analyzing with anonymize=true, use the download_url from the response
    to download the masked file from the 'downloaded' folder.
    """
    # Build file path from downloaded folder
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found. It may have been deleted or never created.")
    
    # Determine media type from extension
    file_ext = os.path.splitext(filename)[1].lower()
    media_types = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp',
        '.csv': 'text/csv'
    }
    media_type = media_types.get(file_ext, 'application/octet-stream')
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


def main():
    """Run the API server"""
    print("\n🚀 Starting Presidio PII Analyzer API Server...")
    print("📝 Note: Analyzer engines will load on first startup (may take 10-15 seconds)")
    print("⚡ Subsequent requests will be FAST as engines are reused!\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )


if __name__ == "__main__":
    main()

