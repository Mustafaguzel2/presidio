#!/usr/bin/env python3
"""
Presidio PII Analyzer - Main Application
Analyzes PDF, Image, and CSV files for Personally Identifiable Information (PII)
"""

import argparse
import json
import sys
import os
from pathlib import Path
from colorama import Fore, Style, init

from analyzers.pdf_analyzer import PDFAnalyzer
from analyzers.image_analyzer import ImageAnalyzer
from analyzers.csv_analyzer import CSVAnalyzer
from maskers.pdf_masker import PDFMasker
from maskers.image_masker import ImageMasker

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)


class PresidioAnalyzerCLI:
    """Command-line interface for PII analysis"""
    
    def __init__(self):
        self.pdf_analyzer = None
        self.image_analyzer = None
        self.csv_analyzer = None
        self.pdf_masker = None
        self.image_masker = None
    
    def get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.csv']:
            return 'csv'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
            return 'image'
        else:
            return 'unknown'
    
    def print_header(self):
        """Print application header"""
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}  Presidio PII Analyzer")
        print(f"{Fore.CYAN}  Analyze PDF, Images, and CSV files for PII")
        print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")
    
    def print_results_summary(self, results: dict, file_type: str):
        """Print a summary of analysis results"""
        print(f"\n{Fore.GREEN}Analysis Results:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
        
        if file_type == 'csv':
            summary = results.get('summary', {})
            analysis = results.get('analysis', {})
            
            print(f"File: {results.get('file_path')}")
            print(f"Total Rows: {analysis.get('total_rows', 0)}")
            print(f"Total Columns: {analysis.get('total_columns', 0)}")
            print(f"Analyzed Rows: {analysis.get('analyzed_rows', 0)}")
            print(f"\n{Fore.RED}PII Summary:{Style.RESET_ALL}")
            print(f"  Columns with PII: {summary.get('columns_with_pii', 0)}")
            print(f"  Total PII instances: {summary.get('total_pii_instances', 0)}")
            
            # Show details for each column with PII
            column_results = analysis.get('column_results', {})
            for column, col_data in column_results.items():
                if col_data['has_pii']:
                    print(f"\n{Fore.CYAN}Column: {column}{Style.RESET_ALL}")
                    print(f"  PII Count: {col_data['pii_count']} row(s)")
                    print(f"  PII Types Detected: {', '.join(col_data['pii_types'].keys())}")
                    
                    # Show ALL findings with entity type and original value
                    all_findings = col_data.get('all_findings', [])
                    if all_findings:
                        print(f"  {Fore.YELLOW}Detailed Findings:{Style.RESET_ALL}")
                        for finding in all_findings:
                            row_idx = finding['row_index']
                            original_value = finding['value']
                            print(f"\n    {Fore.WHITE}Row {row_idx}: {Fore.CYAN}{original_value}{Style.RESET_ALL}")
                            for pii in finding['pii_findings']:
                                entity_type = pii['entity_type']
                                detected_text = pii['text']
                                confidence = pii['score']
                                print(f"      → {Fore.RED}{entity_type}{Style.RESET_ALL}: \"{detected_text}\" (confidence: {confidence:.2f})")
        
        else:  # PDF or Image
            print(f"File: {results.get('file_path')}")
            print(f"PII Found: {Fore.RED if results.get('pii_found') else Fore.GREEN}{results.get('pii_found')}{Style.RESET_ALL}")
            print(f"Total PII Instances: {results.get('pii_count', 0)}")
            
            if results.get('pii_findings'):
                print(f"\n{Fore.CYAN}PII Details:{Style.RESET_ALL}")
                
                # Group by entity type
                pii_by_type = {}
                for finding in results['pii_findings']:
                    entity_type = finding['entity_type']
                    if entity_type not in pii_by_type:
                        pii_by_type[entity_type] = []
                    pii_by_type[entity_type].append(finding)
                
                for entity_type, findings in pii_by_type.items():
                    print(f"\n  {Fore.YELLOW}{entity_type}:{Style.RESET_ALL}")
                    for finding in findings[:5]:  # Show first 5 of each type
                        print(f"    - {finding['text']} (confidence: {finding['score']:.2f})")
                    
                    if len(findings) > 5:
                        print(f"    ... and {len(findings) - 5} more")
        
        print(f"\n{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}\n")
    
    def analyze_file(self, file_path: str, anonymize: bool = False, 
                     output_file: str = None, output_json: str = None,
                     sample_size: int = None, threshold: float = 0.35,
                     output_format: str = 'text', entities: list = None) -> dict:
        """
        Analyze a file for PII
        
        Args:
            file_path: Path to file to analyze
            anonymize: Whether to generate anonymized version
            output_file: Path for anonymized output (CSV/TXT)
            output_json: Path to save JSON results
            sample_size: Sample size for CSV analysis
            threshold: Minimum confidence score (0.0-1.0)
            output_format: Output format ('text' or 'json')
            entities: List of entity types to detect (None = all entities)
            
        Returns:
            Analysis results dictionary
        """
        if not os.path.exists(file_path):
            if output_format != 'json':
                print(f"{Fore.RED}Error: File not found: {file_path}{Style.RESET_ALL}")
            return None
        
        file_type = self.get_file_type(file_path)
        
        if file_type == 'unknown':
            if output_format != 'json':
                print(f"{Fore.RED}Error: Unsupported file type{Style.RESET_ALL}")
            return None
        
        if output_format != 'json':
            print(f"{Fore.CYAN}Analyzing {file_type.upper()} file: {file_path}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please wait...{Style.RESET_ALL}\n")
        
        try:
            if file_type == 'pdf':
                if not self.pdf_analyzer:
                    self.pdf_analyzer = PDFAnalyzer()
                results = self.pdf_analyzer.analyze_pdf(file_path, anonymize=anonymize, threshold=threshold, entities=entities)
                results['file_type'] = 'pdf'
                results['entities_filter'] = entities if entities else 'all'
                
                if anonymize:
                    # Generate output filename if not provided
                    if not output_file:
                        base_name = os.path.splitext(file_path)[0]
                        output_file = f"{base_name}_masked.pdf"
                    
                    # Create masked PDF
                    if not self.pdf_masker:
                        self.pdf_masker = PDFMasker()
                    
                    anonymized_text = results.get('anonymized_text', results['original_text'])
                    self.pdf_masker.create_masked_pdf(file_path, anonymized_text, output_file)
                    if output_format != 'json':
                        print(f"{Fore.GREEN}✓ Masked PDF saved to: {output_file}{Style.RESET_ALL}")
                    results['masked_file'] = output_file
            
            elif file_type == 'image':
                if not self.image_analyzer:
                    self.image_analyzer = ImageAnalyzer()
                results = self.image_analyzer.analyze_image(file_path, anonymize=anonymize, threshold=threshold, entities=entities)
                results['file_type'] = 'image'
                results['entities_filter'] = entities if entities else 'all'
                
                if anonymize:
                    # Generate output filename if not provided
                    if not output_file:
                        base_name = os.path.splitext(file_path)[0]
                        ext = os.path.splitext(file_path)[1]
                        output_file = f"{base_name}_masked{ext}"
                    
                    # Create masked image
                    if not self.image_masker:
                        self.image_masker = ImageMasker()
                    
                    pii_findings = results.get('pii_findings', [])
                    if pii_findings:
                        self.image_masker.create_masked_image(file_path, pii_findings, output_file)
                        if output_format != 'json':
                            print(f"{Fore.GREEN}✓ Masked image saved to: {output_file}{Style.RESET_ALL}")
                        results['masked_file'] = output_file
                    else:
                        if output_format != 'json':
                            print(f"{Fore.YELLOW}No PII to mask in image{Style.RESET_ALL}")
            
            elif file_type == 'csv':
                if not self.csv_analyzer:
                    self.csv_analyzer = CSVAnalyzer()
                
                # Generate output filename if not provided
                if anonymize and not output_file:
                    base_name = os.path.splitext(file_path)[0]
                    output_file = f"{base_name}_masked.csv"
                
                results = self.csv_analyzer.analyze_csv(
                    file_path, 
                    anonymize=anonymize,
                    output_path=output_file,
                    sample_size=sample_size,
                    threshold=threshold,
                    entities=entities
                )
                results['file_type'] = 'csv'
                results['entities_filter'] = entities if entities else 'all'
                
                if anonymize and output_file:
                    if output_format != 'json':
                        print(f"{Fore.GREEN}✓ Masked CSV saved to: {output_file}{Style.RESET_ALL}")
                    results['masked_file'] = output_file
            
            # Save JSON results if requested
            if output_json:
                # Remove large text fields for JSON output
                json_results = results.copy()
                if 'original_text' in json_results:
                    json_results['original_text'] = f"<{len(json_results['original_text'])} characters>"
                if 'anonymized_text' in json_results:
                    json_results['anonymized_text'] = f"<{len(json_results['anonymized_text'])} characters>"
                if 'extracted_text' in json_results:
                    json_results['extracted_text'] = f"<{len(json_results['extracted_text'])} characters>"
                
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(json_results, f, indent=2, default=str)
                if output_format != 'json':
                    print(f"{Fore.GREEN}Results saved to JSON: {output_json}{Style.RESET_ALL}")
            
            return results
        
        except Exception as e:
            if output_format != 'json':
                print(f"{Fore.RED}Error during analysis: {str(e)}{Style.RESET_ALL}")
                import traceback
                traceback.print_exc()
            return None
    
    def run(self):
        """Run the CLI application"""
        parser = argparse.ArgumentParser(
            description='Presidio PII Analyzer - Detect PII in PDF, Images, and CSV files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Analyze a PDF file
  python main.py file.pdf
  
  # Analyze and mask (auto-generates output file: file_masked.pdf)
  python main.py file.pdf --anonymize
  
  # Analyze and mask with custom output
  python main.py file.pdf --anonymize --output secure_file.pdf
  
  # Mask image with black boxes over PII
  python main.py photo.jpg --anonymize
  
  # Mask CSV data (creates data_masked.csv)
  python main.py data.csv --anonymize
  
  # Analyze with custom confidence threshold
  python main.py file.pdf --threshold 0.5
  
  # Detect only specific entity types
  python main.py file.pdf --entities PERSON EMAIL_ADDRESS PHONE_NUMBER
  
  # Output results as JSON to stdout
  python main.py file.pdf --format json
  
  # Detect only emails and mask them
  python main.py data.csv --entities EMAIL_ADDRESS --anonymize
  
  # Complete workflow: analyze, mask, and save JSON report
  python main.py data.csv --anonymize --json report.json
  
  # Large CSV with sampling
  python main.py large_data.csv --sample-size 1000 --anonymize
  
  # JSON output for scripting/automation
  python main.py data.csv --format json > results.json
            """
        )
        
        parser.add_argument('file', help='File to analyze (PDF, Image, or CSV)')
        parser.add_argument('-a', '--anonymize', action='store_true',
                          help='Generate anonymized version of the file')
        parser.add_argument('-o', '--output', help='Output file path for anonymized content')
        parser.add_argument('-j', '--json', help='Save results to JSON file')
        parser.add_argument('-s', '--sample-size', type=int,
                          help='Sample size for CSV analysis (useful for large files)')
        parser.add_argument('-t', '--threshold', type=float, default=0.35,
                          help='Minimum confidence score (0.0-1.0, default: 0.35)')
        parser.add_argument('-e', '--entities', nargs='+',
                          help='Entity types to detect (e.g., PERSON EMAIL_ADDRESS PHONE_NUMBER). If not specified, all entities are detected.')
        parser.add_argument('--no-summary', action='store_true',
                          help='Skip printing results summary to console')
        parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                          help='Output format: text (default) or json')
        
        args = parser.parse_args()
        
        # Don't print header for JSON format
        if args.format != 'json':
            self.print_header()
        
        # Analyze file
        results = self.analyze_file(
            args.file,
            anonymize=args.anonymize,
            output_file=args.output,
            output_json=args.json,
            sample_size=args.sample_size,
            threshold=args.threshold,
            output_format=args.format,
            entities=args.entities
        )
        
        if results:
            if args.format == 'json':
                # Output results as JSON to stdout
                json_results = results.copy()
                # Remove large text fields for cleaner JSON output
                if 'original_text' in json_results and len(json_results.get('original_text', '')) > 500:
                    json_results['original_text'] = f"<{len(json_results['original_text'])} characters>"
                if 'anonymized_text' in json_results and len(json_results.get('anonymized_text', '')) > 500:
                    json_results['anonymized_text'] = f"<{len(json_results['anonymized_text'])} characters>"
                if 'extracted_text' in json_results and len(json_results.get('extracted_text', '')) > 500:
                    json_results['extracted_text'] = f"<{len(json_results['extracted_text'])} characters>"
                
                print(json.dumps(json_results, indent=2, default=str))
            elif not args.no_summary:
                file_type = self.get_file_type(args.file)
                self.print_results_summary(results, file_type)
        
        if results:
            if args.format != 'json':
                print(f"{Fore.GREEN}✓ Analysis complete!{Style.RESET_ALL}\n")
            return 0
        else:
            if args.format != 'json':
                print(f"{Fore.RED}✗ Analysis failed!{Style.RESET_ALL}\n")
            return 1


def main():
    """Main entry point"""
    cli = PresidioAnalyzerCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()

