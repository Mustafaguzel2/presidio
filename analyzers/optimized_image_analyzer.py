"""
Optimized Image Analyzer Module (Uses Singleton)
Analyzes images for PII using OCR and shared Presidio engines
"""

import pytesseract
from PIL import Image
from typing import List, Dict, Any
from .singleton_analyzers import get_analyzer_singleton


class OptimizedImageAnalyzer:
    """
    Analyzes images for Personally Identifiable Information (PII) using OCR.
    Uses singleton pattern for shared Presidio engines - much faster for APIs!
    """
    
    def __init__(self):
        """Initialize with shared analyzer engines"""
        self.singleton = get_analyzer_singleton()
        self.analyzer = self.singleton.analyzer
        self.anonymizer = self.singleton.anonymizer
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR (Tesseract)
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as a string
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get basic information about the image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image metadata
        """
        try:
            image = Image.open(image_path)
            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_text(self, text: str, language: str = "en", threshold: float = 0.35,
                     entities: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze text for PII using Presidio (shared engine)
        
        Args:
            text: Text to analyze
            language: Language code (default: "en")
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            List of detected PII entities
        """
        if not text or not text.strip():
            return []
        
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=entities,
            score_threshold=threshold
        )
        
        # Convert results to dictionaries for better readability
        pii_findings = []
        for result in results:
            pii_findings.append({
                "entity_type": result.entity_type,
                "text": text[result.start:result.end],
                "start": result.start,
                "end": result.end,
                "score": result.score
            })
        
        return pii_findings
    
    def anonymize_text(self, text: str, analyzer_results: List) -> str:
        """
        Anonymize detected PII in text
        
        Args:
            text: Original text
            analyzer_results: Results from analyze_text
            
        Returns:
            Anonymized text
        """
        if not analyzer_results:
            return text
        
        # Convert dict results back to RecognizerResult objects if needed
        from presidio_analyzer import RecognizerResult
        
        if isinstance(analyzer_results[0], dict):
            recognizer_results = [
                RecognizerResult(
                    entity_type=result["entity_type"],
                    start=result["start"],
                    end=result["end"],
                    score=result["score"]
                )
                for result in analyzer_results
            ]
        else:
            recognizer_results = analyzer_results
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=recognizer_results
        )
        
        return anonymized_result.text
    
    def analyze_image(self, image_path: str, anonymize: bool = False, threshold: float = 0.35,
                      entities: List[str] = None) -> Dict[str, Any]:
        """
        Complete image analysis workflow
        
        Args:
            image_path: Path to the image file
            anonymize: Whether to generate anonymized version
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Dictionary containing analysis results
        """
        # Get image info
        image_info = self.get_image_info(image_path)
        
        # Extract text via OCR
        text = self.extract_text_from_image(image_path)
        
        # Analyze for PII
        pii_findings = self.analyze_text(text, threshold=threshold, entities=entities)
        
        result = {
            "file_path": image_path,
            "image_info": image_info,
            "extracted_text": text,
            "pii_found": len(pii_findings) > 0,
            "pii_count": len(pii_findings),
            "pii_findings": pii_findings
        }
        
        # Anonymize if requested
        if anonymize and pii_findings:
            anonymized_text = self.anonymize_text(text, pii_findings)
            result["anonymized_text"] = anonymized_text
        
        return result

