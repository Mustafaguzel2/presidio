# Presidio PII Analyzer - API Guide

## 🚀 Quick Start

### Installation

```bash
# Install API dependencies
pip install fastapi uvicorn[standard] python-multipart

# Or install all requirements
pip install -r requirements.txt
```

### Start the API Server

```bash
# Start the server
python api.py

# Or with uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000
```

**First Startup**: The analyzer engines load on startup (10-15 seconds). This happens only once!

**Subsequent Requests**: Lightning fast! ⚡ Engines are reused for all requests.

### Access the API

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

---

## 📚 API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and engines are loaded.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "analyzer_loaded": true,
  "supported_entities": ["PERSON", "EMAIL_ADDRESS", ...]
}
```

---

### 2. Get Supported Entities

**GET** `/api/entities`

Get list of all PII entity types that can be detected.

```bash
curl http://localhost:8000/api/entities
```

**Response:**
```json
{
  "total": 25,
  "entities": ["CREDIT_CARD", "EMAIL_ADDRESS", "PERSON", ...],
  "common_entities": [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
    "US_SSN", "LOCATION", "DATE_TIME", "IP_ADDRESS", "URL"
  ]
}
```

---

### 3. Analyze Text

**POST** `/api/analyze/text`

Analyze plain text for PII.

**Parameters:**
- `text` (required): Text to analyze
- `threshold` (optional): Confidence threshold (0.0-1.0, default: 0.35)
- `entities` (optional): Comma-separated entity types (e.g., "PERSON,EMAIL_ADDRESS")

**Example:**

```bash
curl -X POST "http://localhost:8000/api/analyze/text" \
  -F "text=My name is John Doe and my email is john@example.com" \
  -F "threshold=0.35" \
  -F "entities=PERSON,EMAIL_ADDRESS"
```

**Response:**
```json
{
  "pii_found": true,
  "pii_count": 2,
  "pii_findings": [
    {
      "entity_type": "PERSON",
      "text": "John Doe",
      "start": 11,
      "end": 19,
      "score": 0.85
    },
    {
      "entity_type": "EMAIL_ADDRESS",
      "text": "john@example.com",
      "start": 37,
      "end": 53,
      "score": 1.0
    }
  ],
  "entities_filter": "PERSON,EMAIL_ADDRESS"
}
```

---

### 4. Analyze PDF

**POST** `/api/analyze/pdf`

Analyze PDF file for PII.

**Parameters:**
- `file` (required): PDF file upload
- `threshold` (optional): Confidence threshold (default: 0.35)
- `entities` (optional): Comma-separated entity types
- `anonymize` (optional): Create masked version (default: false)

**Example:**

```bash
curl -X POST "http://localhost:8000/api/analyze/pdf" \
  -F "file=@document.pdf" \
  -F "threshold=0.4" \
  -F "entities=PERSON,EMAIL_ADDRESS,PHONE_NUMBER" \
  -F "anonymize=true"
```

**Response:**
```json
{
  "file_path": "/tmp/document.pdf",
  "file_type": "pdf",
  "pii_found": true,
  "pii_count": 15,
  "pii_findings": [...],
  "entities_filter": ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
  "download_url": "/api/download/masked_document.pdf"
}
```

---

### 5. Analyze Image

**POST** `/api/analyze/image`

Analyze image file for PII using OCR.

**Parameters:**
- `file` (required): Image file (PNG, JPG, etc.)
- `threshold` (optional): Confidence threshold (default: 0.35)
- `entities` (optional): Comma-separated entity types
- `anonymize` (optional): Create masked version (default: false)

**Example:**

```bash
curl -X POST "http://localhost:8000/api/analyze/image" \
  -F "file=@screenshot.png" \
  -F "threshold=0.35" \
  -F "anonymize=true"
```

**Response:**
```json
{
  "file_path": "/tmp/screenshot.png",
  "file_type": "image",
  "image_info": {
    "format": "PNG",
    "mode": "RGB",
    "size": [1920, 1080],
    "width": 1920,
    "height": 1080
  },
  "extracted_text": "Contact: john@example.com",
  "pii_found": true,
  "pii_count": 1,
  "pii_findings": [...],
  "download_url": "/api/download/masked_screenshot.png"
}
```

---

### 6. Analyze CSV

**POST** `/api/analyze/csv`

Analyze CSV file for PII.

**Parameters:**
- `file` (required): CSV file upload
- `threshold` (optional): Confidence threshold (default: 0.35)
- `entities` (optional): Comma-separated entity types
- `sample_size` (optional): Number of rows to sample for large files
- `anonymize` (optional): Create masked version (default: false)

**Example:**

```bash
curl -X POST "http://localhost:8000/api/analyze/csv" \
  -F "file=@contacts.csv" \
  -F "threshold=0.35" \
  -F "entities=EMAIL_ADDRESS,PHONE_NUMBER" \
  -F "sample_size=1000" \
  -F "anonymize=true"
```

**Response:**
```json
{
  "file_path": "/tmp/contacts.csv",
  "file_type": "csv",
  "analysis": {
    "total_columns": 5,
    "total_rows": 10000,
    "analyzed_rows": 1000,
    "is_sampled": true,
    "column_results": {
      "Email": {
        "has_pii": true,
        "pii_count": 1000,
        "pii_types": {"EMAIL_ADDRESS": 1000}
      }
    }
  },
  "summary": {
    "columns_with_pii": 2,
    "total_pii_instances": 1500
  },
  "download_url": "/api/download/masked_contacts.csv"
}
```

---

### 7. Download File

**GET** `/api/download/{filename}`

Download anonymized file.

**Example:**

```bash
curl -O "http://localhost:8000/api/download/masked_document.pdf"
```

---

## 🔧 Python Client Examples

### Using `requests` Library

```python
import requests

# Analyze text
response = requests.post(
    "http://localhost:8000/api/analyze/text",
    data={
        "text": "Contact John Doe at john@example.com or call +1-555-0123",
        "threshold": 0.35,
        "entities": "PERSON,EMAIL_ADDRESS,PHONE_NUMBER"
    }
)
result = response.json()
print(f"Found {result['pii_count']} PII instances")

# Analyze PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze/pdf",
        files={"file": f},
        data={
            "threshold": 0.4,
            "entities": "PERSON,EMAIL_ADDRESS",
            "anonymize": "true"
        }
    )
result = response.json()

# Download masked file if available
if "download_url" in result:
    download_url = f"http://localhost:8000{result['download_url']}"
    masked_file = requests.get(download_url)
    with open("masked_document.pdf", "wb") as f:
        f.write(masked_file.content)
```

### Using `httpx` (Async)

```python
import httpx
import asyncio

async def analyze_files():
    async with httpx.AsyncClient() as client:
        # Analyze multiple files concurrently
        tasks = []
        
        for filename in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
            with open(filename, "rb") as f:
                task = client.post(
                    "http://localhost:8000/api/analyze/pdf",
                    files={"file": (filename, f, "application/pdf")},
                    data={"threshold": 0.35}
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return [r.json() for r in results]

# Run
results = asyncio.run(analyze_files())
```

---

## 🎯 Use Cases

### 1. Data Compliance Pipeline

```python
import requests

def check_compliance(file_path: str) -> dict:
    """Check if file contains regulated PII"""
    
    # Only check for regulated entities
    regulated_entities = "US_SSN,CREDIT_CARD,US_PASSPORT,MEDICAL_LICENSE"
    
    with open(file_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/analyze/pdf",
            files={"file": f},
            data={
                "entities": regulated_entities,
                "threshold": 0.5  # High confidence only
            }
        )
    
    result = response.json()
    return {
        "compliant": not result["pii_found"],
        "violations": result["pii_count"],
        "details": result["pii_findings"]
    }
```

### 2. Automated Document Sanitization

```python
def sanitize_document(input_path: str, output_path: str):
    """Automatically mask PII in documents"""
    
    with open(input_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/analyze/pdf",
            files={"file": f},
            data={
                "anonymize": "true",
                "threshold": 0.35
            }
        )
    
    result = response.json()
    
    # Download masked version
    if result.get("download_url"):
        masked = requests.get(f"http://localhost:8000{result['download_url']}")
        with open(output_path, "wb") as f:
            f.write(masked.content)
        
        return {"success": True, "pii_removed": result["pii_count"]}
    
    return {"success": False, "message": "No PII found"}
```

### 3. Batch Processing

```python
import os
from concurrent.futures import ThreadPoolExecutor

def process_directory(directory: str):
    """Process all PDFs in a directory"""
    
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    
    def process_file(filename):
        filepath = os.path.join(directory, filename)
        with open(filepath, "rb") as f:
            response = requests.post(
                "http://localhost:8000/api/analyze/pdf",
                files={"file": f},
                data={"threshold": 0.35}
            )
        return {
            "file": filename,
            "result": response.json()
        }
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_file, pdf_files))
    
    return results
```

---

## ⚡ Performance Optimization

### Why This API is Fast

1. **Singleton Pattern**: Analyzer engines load once at startup
2. **Shared Resources**: All requests use the same Spacy NER model
3. **No Re-initialization**: No model loading overhead per request

### Performance Comparison

| Approach | First Request | Subsequent Requests |
|----------|---------------|---------------------|
| **Old (CLI)** | ~15 seconds | ~15 seconds (reloads every time) |
| **New (API)** | ~15 seconds | **~0.1-2 seconds** ⚡ |

### Optimization Tips

```python
# 1. Use entity filtering to speed up analysis
requests.post(
    url,
    data={"entities": "EMAIL_ADDRESS"}  # Much faster than all entities
)

# 2. Use sampling for large CSVs
requests.post(
    url,
    data={"sample_size": 1000}  # Analyze subset
)

# 3. Batch process with concurrent requests
# Use ThreadPoolExecutor or asyncio for parallel processing
```

---

## 🔒 Security Considerations

### Production Deployment

1. **Authentication**: Add API keys or OAuth
   ```python
   from fastapi import Header, HTTPException
   
   async def verify_token(x_api_key: str = Header(...)):
       if x_api_key != "your-secret-key":
           raise HTTPException(status_code=401)
   ```

2. **Rate Limiting**: Prevent abuse
   ```bash
   pip install slowapi
   ```

3. **File Size Limits**: Prevent large uploads
   ```python
   from fastapi import File, UploadFile
   
   MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
   ```

4. **HTTPS**: Use SSL in production
   ```bash
   uvicorn api:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

5. **File Cleanup**: Implement proper temp file management
   ```python
   from fastapi import BackgroundTasks
   
   def cleanup_file(path: str):
       os.remove(path)
   
   @app.post("/api/analyze/pdf")
   async def analyze(file: UploadFile, background_tasks: BackgroundTasks):
       # ... processing ...
       background_tasks.add_task(cleanup_file, temp_path)
   ```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy model
RUN python -m spacy download en_core_web_lg

# Copy application
COPY . .

EXPOSE 8000

CMD ["python", "api.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  presidio-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WORKERS=4
    volumes:
      - ./temp:/tmp
    restart: unless-stopped
```

### Build and Run

```bash
# Build
docker build -t presidio-api .

# Run
docker run -p 8000:8000 presidio-api

# Or with docker-compose
docker-compose up -d
```

---

## 📊 Monitoring

### Health Check Endpoint

```bash
# Check if API is healthy
curl http://localhost:8000/health

# Use in monitoring tools
*/5 * * * * curl -f http://localhost:8000/health || alert
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🎓 Advanced Usage

### Custom Entity Recognizer

```python
from presidio_analyzer import Pattern, PatternRecognizer
from analyzers.singleton_analyzers import get_analyzer_singleton

# Add custom recognizer
singleton = get_analyzer_singleton()

custom_recognizer = PatternRecognizer(
    supported_entity="CUSTOM_ID",
    patterns=[Pattern("custom_pattern", r"\bCUST-\d{6}\b", 0.8)]
)

singleton.analyzer.registry.add_recognizer(custom_recognizer)
```

### Webhook Integration

```python
import requests

@app.post("/api/analyze/pdf")
async def analyze_with_webhook(
    file: UploadFile,
    webhook_url: str = Form(None)
):
    # ... analysis ...
    
    # Send results to webhook
    if webhook_url:
        requests.post(webhook_url, json=results)
    
    return results
```

---

## 🔍 Troubleshooting

### Common Issues

**1. "AnalyzerEngine not initialized"**
- Solution: Wait for startup to complete
- Check logs for initialization errors

**2. Slow first request**
- Normal! Model loads on startup (10-15s)
- Subsequent requests are fast

**3. Out of memory**
- Reduce batch size
- Use sampling for large CSVs
- Increase server memory

**4. OCR not working**
- Install Tesseract: `apt-get install tesseract-ocr`
- Check image quality

---

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Supported Entities**: http://localhost:8000/api/entities

---

**Happy PII Detection! 🔒**

