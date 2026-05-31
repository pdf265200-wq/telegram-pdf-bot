import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path
from typing import List, Optional
import os

from config import Config

class OCRService:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
    
    async def extract_text_from_image(self, image_path: str, languages: List[str] = None) -> str:
        """Extract text from image using OCR"""
        if not languages:
            languages = Config.OCR_LANGUAGES
        
        image = Image.open(image_path)
        lang_string = '+'.join(languages)
        
        text = pytesseract.image_to_string(image, lang=lang_string)
        return text
    
    async def extract_text_from_pdf(self, pdf_path: str, languages: List[str] = None) -> str:
        """Extract text from scanned PDF"""
        if not languages:
            languages = Config.OCR_LANGUAGES
        
        images = convert_from_path(pdf_path)
        full_text = ''
        
        for i, image in enumerate(images):
            lang_string = '+'.join(languages)
            text = pytesseract.image_to_string(image, lang=lang_string)
            full_text += f'--- Page {i+1} ---\n{text}\n\n'
        
        return full_text
    
    async def create_searchable_pdf(self, pdf_path: str, languages: List[str] = None, output_path: Optional[str] = None) -> str:
        """Create searchable PDF from scanned document"""
        if not languages:
            languages = Config.OCR_LANGUAGES
        
        if not output_path:
            from utils.helpers import generate_temp_filename
            output_path = generate_temp_filename('.pdf')
        
        # Use pikepdf to create searchable PDF
        import pikepdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        images = convert_from_path(pdf_path)
        
        # Create PDF with OCR text layer
        c = canvas.Canvas(output_path)
        
        for i, image in enumerate(images):
            # Convert image to PDF page
            img_temp = io.BytesIO()
            image.save(img_temp, format='PDF')
            img_temp.seek(0)
            
            # Add image
            c.drawImage(img_temp, 0, 0, width=letter[0], height=letter[1])
            
            # Add invisible text layer for searching
            text = pytesseract.image_to_string(image, lang='+'.join(languages))
            c.setFillColorRGB(1, 1, 1, alpha=0)  # Transparent text
            c.drawString(0, 0, text)
            
            if i < len(images) - 1:
                c.showPage()
        
        c.save()
        return output_path
    
    async def extract_text_arabic(self, image_path: str) -> str:
        """Extract Arabic text from image"""
        return await self.extract_text_from_image(image_path, languages=['ara'])
    
    async def extract_text_english(self, image_path: str) -> str:
        """Extract English text from image"""
        return await self.extract_text_from_image(image_path, languages=['eng'])

# Global service instance
ocr_service = OCRService()
