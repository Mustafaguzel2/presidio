"""
Singleton Analyzers Module
Provides shared analyzer instances that are initialized once and reused
"""

import threading
from typing import Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class AnalyzerSingleton:
    """
    Singleton class for Presidio Analyzer and Anonymizer engines.
    Ensures engines are loaded only once and shared across all requests.
    This significantly improves performance for API usage.
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AnalyzerSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Presidio engines only once"""
        if not AnalyzerSingleton._initialized:
            with AnalyzerSingleton._lock:
                if not AnalyzerSingleton._initialized:
                    print("🔄 Initializing Presidio engines (one-time operation)...")
                    self._analyzer_engine: Optional[AnalyzerEngine] = None
                    self._anonymizer_engine: Optional[AnonymizerEngine] = None
                    self._load_engines()
                    AnalyzerSingleton._initialized = True
                    print("✅ Presidio engines initialized and ready!")
    
    def _load_engines(self):
        """Load Presidio analyzer and anonymizer engines"""
        try:
            # Initialize Presidio engines (loads Spacy model internally)
            self._analyzer_engine = AnalyzerEngine()
            self._anonymizer_engine = AnonymizerEngine()
            
            # Warm up the engines with a test text to ensure model is loaded
            test_results = self._analyzer_engine.analyze(
                text="John Doe john@example.com",
                language="en",
                entities=None
            )
            print(f"   Model warm-up complete. Detected {len(test_results)} entities in test.")
            
        except Exception as e:
            print(f"❌ Error loading Presidio engines: {str(e)}")
            raise
    
    @property
    def analyzer(self) -> AnalyzerEngine:
        """Get the shared analyzer engine instance"""
        if self._analyzer_engine is None:
            raise RuntimeError("AnalyzerEngine not initialized")
        return self._analyzer_engine
    
    @property
    def anonymizer(self) -> AnonymizerEngine:
        """Get the shared anonymizer engine instance"""
        if self._anonymizer_engine is None:
            raise RuntimeError("AnonymizerEngine not initialized")
        return self._anonymizer_engine
    
    def get_supported_entities(self):
        """Get list of all supported entity types"""
        return self.analyzer.get_supported_entities(language="en")


# Global function to get singleton instance
_singleton_instance = None

def get_analyzer_singleton() -> AnalyzerSingleton:
    """
    Get the global singleton instance of analyzers.
    This function ensures thread-safe access to the singleton.
    """
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = AnalyzerSingleton()
    return _singleton_instance

