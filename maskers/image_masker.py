"""
Image Masker Module
Creates masked images with PII redacted using black boxes
"""

from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pytesseract import Output
from typing import List, Dict, Any


class ImageMasker:
    """Creates masked images with PII redacted"""
    
    def get_text_boxes(self, image_path: str) -> Dict:
        """
        Get bounding boxes for all text in image using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with text locations
        """
        image = Image.open(image_path)
        # Get detailed OCR data including bounding boxes
        ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)
        return ocr_data
    
    def find_text_positions(self, ocr_data: Dict, text_to_mask: str) -> List[Dict[str, int]]:
        """
        Find positions of specific text in OCR data
        
        Args:
            ocr_data: OCR data from pytesseract
            text_to_mask: Text string to find and mask
            
        Returns:
            List of bounding boxes for the text
        """
        positions = []
        n_boxes = len(ocr_data['text'])
        
        # Normalize text for comparison
        normalized_target = ''.join(text_to_mask.split()).lower()
        
        for i in range(n_boxes):
            word = ocr_data['text'][i].strip()
            if word:
                normalized_word = word.lower()
                # Check if this word is part of the text to mask
                if normalized_word in normalized_target or normalized_target in normalized_word:
                    x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                                 ocr_data['width'][i], ocr_data['height'][i])
                    positions.append({'x': x, 'y': y, 'width': w, 'height': h})
        
        return positions
    
    def create_masked_image(self, image_path: str, pii_findings: List[Dict[str, Any]], 
                           output_path: str, mask_color: str = 'black'):
        """
        Create masked image with black boxes over PII
        
        Args:
            image_path: Path to original image
            pii_findings: List of PII detections
            output_path: Path to save masked image
            mask_color: Color for masking (default: black)
        """
        # Open image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Get OCR data for text positions
        ocr_data = self.get_text_boxes(image_path)
        
        # Mask each PII finding
        for finding in pii_findings:
            text_to_mask = finding['text']
            
            # Find positions of this text in the image
            positions = self.find_text_positions(ocr_data, text_to_mask)
            
            # Draw black rectangles over each position
            for pos in positions:
                x1 = pos['x']
                y1 = pos['y']
                x2 = x1 + pos['width']
                y2 = y1 + pos['height']
                
                # Add some padding
                padding = 2
                draw.rectangle(
                    [x1-padding, y1-padding, x2+padding, y2+padding],
                    fill=mask_color
                )
        
        # Save masked image
        image.save(output_path)

