"""
Optimized PDF Analyzer Module (Uses Singleton)
Analyzes PDF files for PII using shared Presidio engines
"""

import pdfplumber
from typing import List, Dict, Any
from .singleton_analyzers import get_analyzer_singleton


class OptimizedPDFAnalyzer:
    """
    Analyzes PDF files for Personally Identifiable Information (PII).
    Uses singleton pattern for shared Presidio engines - much faster for APIs!
    """
    
    def __init__(self):
        """Initialize with shared analyzer engines"""
        self.singleton = get_analyzer_singleton()
        self.analyzer = self.singleton.analyzer
        self.anonymizer = self.singleton.anonymizer
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return "\n\n".join(text_content)
    
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
        # Convert dict results back to RecognizerResult objects if needed
        from presidio_analyzer import RecognizerResult
        
        if analyzer_results and isinstance(analyzer_results[0], dict):
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
    
    def analyze_pdf(self, pdf_path: str, anonymize: bool = False, threshold: float = 0.35,
                    entities: List[str] = None) -> Dict[str, Any]:
        """
        Complete PDF analysis workflow
        
        Args:
            pdf_path: Path to the PDF file
            anonymize: Whether to generate anonymized version
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Dictionary containing analysis results
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Analyze for PII
        pii_findings = self.analyze_text(text, threshold=threshold, entities=entities)
        
        result = {
            "file_path": pdf_path,
            "original_text": text,
            "pii_found": len(pii_findings) > 0,
            "pii_count": len(pii_findings),
            "pii_findings": pii_findings
        }
        
        # Anonymize if requested
        if anonymize and pii_findings:
            anonymized_text = self.anonymize_text(text, pii_findings)
            result["anonymized_text"] = anonymized_text
        
        return result

