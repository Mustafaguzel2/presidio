"""
PDF Masker Module
Creates masked PDF files with PII replaced
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pdfplumber
from typing import List, Dict
import html


class PDFMasker:
    """Creates masked PDF files with PII redacted"""
    
    def escape_html_entities(self, text: str) -> str:
        """
        Escape HTML entities so angle brackets display correctly
        
        Args:
            text: Text with potential angle brackets
            
        Returns:
            Text with escaped angle brackets
        """
        # Escape < and > to &lt; and &gt; so reportlab displays them
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    def create_masked_pdf(self, original_pdf_path: str, anonymized_text: str, output_path: str):
        """
        Create a new PDF with anonymized text
        
        Args:
            original_pdf_path: Path to original PDF
            anonymized_text: Anonymized text content
            output_path: Path to save masked PDF
        """
        # Create PDF with anonymized text
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Create a custom style for better readability
        custom_style = ParagraphStyle(
            'CustomStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=6,
            spaceAfter=6,
        )
        
        # Escape HTML entities in the anonymized text
        anonymized_text = self.escape_html_entities(anonymized_text)
        
        # Split text into paragraphs
        paragraphs = anonymized_text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                # Replace multiple spaces/newlines with single space but preserve single newlines
                lines = para.split('\n')
                cleaned_lines = [' '.join(line.split()) for line in lines if line.strip()]
                cleaned_para = '<br/>'.join(cleaned_lines)
                
                p = Paragraph(cleaned_para, custom_style)
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)

