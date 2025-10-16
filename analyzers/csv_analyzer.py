"""
CSV Analyzer Module
Analyzes CSV files for PII using Presidio
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class CSVAnalyzer:
    """Analyzes CSV files for Personally Identifiable Information (PII)"""
    
    def __init__(self):
        """Initialize the CSV analyzer with Presidio engines"""
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def read_csv(self, csv_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Read CSV file into a pandas DataFrame
        
        Args:
            csv_path: Path to the CSV file
            encoding: File encoding (default: 'utf-8')
            
        Returns:
            DataFrame containing CSV data
        """
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            return df
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                df = pd.read_csv(csv_path, encoding='latin-1')
                return df
            except Exception as e:
                raise Exception(f"Error reading CSV file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    
    def analyze_text(self, text: str, language: str = "en", threshold: float = 0.35,
                     entities: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze text for PII using Presidio
        
        Args:
            text: Text to analyze
            language: Language code (default: "en")
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            List of detected PII entities
        """
        if not text or pd.isna(text) or str(text).strip() == '':
            return []
        
        text_str = str(text)
        results = self.analyzer.analyze(
            text=text_str,
            language=language,
            entities=entities,  # Detect specified entities or all if None
            score_threshold=threshold
        )
        
        # Convert results to dictionaries for better readability
        pii_findings = []
        for result in results:
            pii_findings.append({
                "entity_type": result.entity_type,
                "text": text_str[result.start:result.end],
                "start": result.start,
                "end": result.end,
                "score": result.score
            })
        
        return pii_findings
    
    def analyze_dataframe(self, df: pd.DataFrame, sample_size: Optional[int] = None, 
                          threshold: float = 0.35, entities: List[str] = None) -> Dict[str, Any]:
        """
        Analyze DataFrame for PII
        
        Args:
            df: DataFrame to analyze
            sample_size: Optional number of rows to sample for large datasets
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Dictionary containing analysis results by column
        """
        if sample_size and len(df) > sample_size:
            df_to_analyze = df.sample(n=sample_size, random_state=42)
            is_sampled = True
        else:
            df_to_analyze = df
            is_sampled = False
        
        column_results = {}
        
        for column in df_to_analyze.columns:
            column_pii = []
            
            for idx, value in enumerate(df_to_analyze[column]):
                if pd.notna(value):
                    pii_findings = self.analyze_text(str(value), threshold=threshold, entities=entities)
                    if pii_findings:
                        column_pii.append({
                            "row_index": df_to_analyze.index[idx],
                            "value": str(value),
                            "pii_findings": pii_findings
                        })
            
            if column_pii:
                # Get PII type summary for this column
                pii_types = {}
                for item in column_pii:
                    for finding in item["pii_findings"]:
                        pii_type = finding["entity_type"]
                        pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                
                column_results[column] = {
                    "has_pii": True,
                    "pii_count": len(column_pii),
                    "pii_types": pii_types,
                    "all_findings": column_pii  # All findings, not just samples
                }
            else:
                column_results[column] = {
                    "has_pii": False,
                    "pii_count": 0,
                    "pii_types": {},
                    "all_findings": []
                }
        
        return {
            "total_columns": len(df.columns),
            "total_rows": len(df),
            "analyzed_rows": len(df_to_analyze),
            "is_sampled": is_sampled,
            "column_results": column_results
        }
    
    def anonymize_dataframe(self, df: pd.DataFrame, threshold: float = 0.35,
                            entities: List[str] = None) -> pd.DataFrame:
        """
        Anonymize PII in DataFrame
        
        Args:
            df: DataFrame to anonymize
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Anonymized DataFrame
        """
        from presidio_analyzer import RecognizerResult
        
        df_anonymized = df.copy()
        
        for column in df_anonymized.columns:
            for idx in df_anonymized.index:
                value = df_anonymized.at[idx, column]
                
                if pd.notna(value):
                    value_str = str(value)
                    pii_findings = self.analyze_text(value_str, threshold=threshold, entities=entities)
                    
                    if pii_findings:
                        # Convert to RecognizerResult objects
                        recognizer_results = [
                            RecognizerResult(
                                entity_type=result["entity_type"],
                                start=result["start"],
                                end=result["end"],
                                score=result["score"]
                            )
                            for result in pii_findings
                        ]
                        
                        # Anonymize
                        anonymized_result = self.anonymizer.anonymize(
                            text=value_str,
                            analyzer_results=recognizer_results
                        )
                        
                        df_anonymized.at[idx, column] = anonymized_result.text
        
        return df_anonymized
    
    def analyze_csv(self, csv_path: str, anonymize: bool = False, 
                    output_path: Optional[str] = None, sample_size: Optional[int] = None, 
                    threshold: float = 0.35, entities: List[str] = None) -> Dict[str, Any]:
        """
        Complete CSV analysis workflow
        
        Args:
            csv_path: Path to the CSV file
            anonymize: Whether to generate anonymized version
            output_path: Path to save anonymized CSV (if anonymize=True)
            sample_size: Optional sample size for large datasets
            threshold: Minimum confidence score (0.0-1.0, default: 0.35)
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Dictionary containing analysis results
        """
        # Read CSV
        df = self.read_csv(csv_path)
        
        # Analyze for PII
        analysis_results = self.analyze_dataframe(df, sample_size=sample_size, threshold=threshold, entities=entities)
        
        result = {
            "file_path": csv_path,
            "analysis": analysis_results
        }
        
        # Get summary statistics
        columns_with_pii = sum(1 for col_result in analysis_results["column_results"].values() 
                              if col_result["has_pii"])
        total_pii_instances = sum(col_result["pii_count"] 
                                 for col_result in analysis_results["column_results"].values())
        
        result["summary"] = {
            "columns_with_pii": columns_with_pii,
            "total_pii_instances": total_pii_instances
        }
        
        # Anonymize if requested
        if anonymize:
            df_anonymized = self.anonymize_dataframe(df, threshold=threshold, entities=entities)
            
            if output_path:
                df_anonymized.to_csv(output_path, index=False)
                result["anonymized_file"] = output_path
            
            result["anonymized_preview"] = df_anonymized.head(10).to_dict()
        
        return result

