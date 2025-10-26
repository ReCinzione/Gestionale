"""
Servizio OCR per l'estrazione di testo da immagini e conversione foto in PDF.
"""

import os
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import pytesseract

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class OCRService:
    """Servizio per OCR e gestione PDF fatture"""
    
    def __init__(self):
        self.tesseract_path = self._find_tesseract()
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def _find_tesseract(self) -> Optional[str]:
        """Trova l'installazione di Tesseract"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
            'tesseract'  # Se è nel PATH
        ]
        
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    return path
                elif path == 'tesseract':
                    # Testa se tesseract è nel PATH
                    import subprocess
                    result = subprocess.run(['tesseract', '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'tesseract'
            except:
                continue
        
        return None
    
    def is_available(self) -> bool:
        """Verifica se OCR è disponibile"""
        return self.tesseract_path is not None
    
    def get_installation_instructions(self) -> str:
        """Restituisce istruzioni per installare Tesseract"""
        return """
Per utilizzare l'OCR, installa Tesseract OCR:

1. Vai su: https://github.com/UB-Mannheim/tesseract/wiki
2. Scarica "tesseract-ocr-w64-setup-5.x.x.exe"
3. Installa in: C:\\Program Files\\Tesseract-OCR
4. Riavvia l'applicazione

Tesseract è gratuito e open source.
"""
    
    def extract_text_from_image(self, image_path: str, language: str = 'ita+eng') -> str:
        """
        Estrae testo da un'immagine usando OCR.
        
        Args:
            image_path: Percorso dell'immagine
            language: Linguaggio OCR (default: italiano + inglese)
            
        Returns:
            Testo estratto
        """
        if not self.is_available():
            raise Exception("Tesseract OCR non disponibile")
        
        try:
            # Apri e preprocessa l'immagine
            image = Image.open(image_path)
            
            # Converti in RGB se necessario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Migliora la qualità per OCR
            image = self._preprocess_image(image)
            
            # Estrai testo
            text = pytesseract.image_to_string(image, lang=language)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Errore durante l'OCR: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocessa l'immagine per migliorare l'OCR"""
        # Ridimensiona se troppo piccola
        width, height = image.size
        if width < 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def create_pdf_from_image(self, image_path: str, output_path: str, 
                             include_ocr: bool = True) -> str:
        """
        Crea un PDF da un'immagine, opzionalmente con testo OCR invisibile.
        
        Args:
            image_path: Percorso dell'immagine
            output_path: Percorso del PDF di output
            include_ocr: Se includere testo OCR invisibile
            
        Returns:
            Testo estratto (se include_ocr=True)
        """
        try:
            # Apri l'immagine
            image = Image.open(image_path)
            
            # Converti in RGB se necessario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Calcola dimensioni per A4
            img_width, img_height = image.size
            a4_width, a4_height = A4
            
            # Scala l'immagine per adattarla ad A4 mantenendo proporzioni
            scale_w = a4_width / img_width
            scale_h = a4_height / img_height
            scale = min(scale_w, scale_h)
            
            new_width = img_width * scale
            new_height = img_height * scale
            
            # Crea il PDF
            c = canvas.Canvas(output_path, pagesize=A4)
            
            # Salva l'immagine temporaneamente
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                image.save(temp_img.name, 'JPEG', quality=95)
                temp_img_path = temp_img.name
            
            try:
                # Aggiungi l'immagine al PDF
                x = (a4_width - new_width) / 2
                y = (a4_height - new_height) / 2
                c.drawImage(temp_img_path, x, y, new_width, new_height)
                
                extracted_text = ""
                
                # Aggiungi testo OCR invisibile se richiesto
                if include_ocr and self.is_available():
                    try:
                        extracted_text = self.extract_text_from_image(image_path)
                        
                        if extracted_text.strip():
                            # Aggiungi testo invisibile per ricerca
                            c.setFillColorRGB(1, 1, 1, alpha=0)  # Trasparente
                            c.setFont("Helvetica", 8)
                            
                            # Dividi il testo in righe e posiziona
                            lines = extracted_text.split('\n')
                            y_text = a4_height - 50
                            
                            for line in lines[:50]:  # Limita a 50 righe
                                if line.strip():
                                    c.drawString(50, y_text, line.strip()[:100])
                                    y_text -= 12
                                    if y_text < 50:
                                        break
                    
                    except Exception as ocr_error:
                        print(f"Errore OCR (continuando senza): {ocr_error}")
                
                c.save()
                return extracted_text
                
            finally:
                # Pulisci file temporaneo
                if os.path.exists(temp_img_path):
                    os.unlink(temp_img_path)
            
        except Exception as e:
            raise Exception(f"Errore creazione PDF: {str(e)}")
    
    def extract_invoice_data(self, text: str) -> Dict[str, str]:
        """
        Estrae dati strutturati da testo di fattura usando regex.
        
        Args:
            text: Testo estratto dalla fattura
            
        Returns:
            Dizionario con dati estratti
        """
        data = {
            'invoice_number': '',
            'date': '',
            'total_amount': '',
            'supplier_name': '',
            'vat_number': ''
        }
        
        # Pulisci il testo
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())  # Rimuovi spazi multipli
        
        # Regex per numero fattura
        invoice_patterns = [
            r'(?:fattura|invoice|n\.?|num\.?|numero)\s*:?\s*([A-Z0-9\-/]+)',
            r'(?:ft|fatt\.?)\s*:?\s*([A-Z0-9\-/]+)',
            r'(?:doc\.?|documento)\s*:?\s*([A-Z0-9\-/]+)'
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['invoice_number'] = match.group(1).strip()
                break
        
        # Regex per data
        date_patterns = [
            r'(?:data|del|date)\s*:?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Prendi la prima data che sembra valida
                for date_str in matches:
                    try:
                        # Prova a parsare la data per validarla
                        parts = re.split(r'[/\-\.]', date_str)
                        if len(parts) == 3:
                            day, month, year = parts
                            if len(year) == 2:
                                year = '20' + year
                            if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
                                data['date'] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                                break
                    except:
                        continue
                if data['date']:
                    break
        
        # Regex per importo totale
        amount_patterns = [
            r'(?:totale|total|importo|euro|eur|€)\s*:?\s*€?\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            r'€\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Prendi l'importo più alto (probabilmente il totale)
                amounts = []
                for amount_str in matches:
                    try:
                        # Normalizza il formato (usa . per decimali)
                        normalized = amount_str.replace(',', '.')
                        # Se ci sono più punti, l'ultimo è decimale
                        if normalized.count('.') > 1:
                            parts = normalized.split('.')
                            normalized = ''.join(parts[:-1]) + '.' + parts[-1]
                        
                        amount = float(normalized)
                        if amount > 0:
                            amounts.append((amount, amount_str))
                    except:
                        continue
                
                if amounts:
                    # Prendi l'importo più alto
                    max_amount = max(amounts, key=lambda x: x[0])
                    data['total_amount'] = max_amount[1]
                    break
        
        # Regex per P.IVA
        vat_patterns = [
            r'(?:p\.?\s*iva|partita\s+iva|vat)\s*:?\s*([0-9]{11})',
            r'(?:pi|p\.i\.)\s*:?\s*([0-9]{11})'
        ]
        
        for pattern in vat_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['vat_number'] = match.group(1).strip()
                break
        
        # Estrai possibile nome fornitore (prime righe del testo)
        lines = text.split()
        if len(lines) > 0:
            # Prendi le prime parole che potrebbero essere il nome
            potential_name = ' '.join(lines[:5])
            # Rimuovi caratteri speciali e numeri
            clean_name = re.sub(r'[^a-zA-Z\s]', '', potential_name)
            clean_name = ' '.join(clean_name.split())
            if len(clean_name) > 3:
                data['supplier_name'] = clean_name[:50]
        
        return data
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Estrae testo da un PDF esistente.
        
        Args:
            pdf_path: Percorso del file PDF
            
        Returns:
            Testo estratto
        """
        if not PYPDF2_AVAILABLE:
            raise Exception("PyPDF2 non disponibile per leggere PDF")
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Errore lettura PDF: {str(e)}")
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """
        Converte le pagine di un PDF in immagini per OCR.
        
        Args:
            pdf_path: Percorso del PDF
            output_dir: Directory per salvare le immagini
            
        Returns:
            Lista dei percorsi delle immagini create
        """
        if not PDF2IMAGE_AVAILABLE:
            raise Exception("pdf2image non disponibile")
        
        try:
            # Converti PDF in immagini
            images = convert_from_path(pdf_path, dpi=300)
            
            image_paths = []
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
                image.save(image_path, 'JPEG', quality=95)
                image_paths.append(image_path)
            
            return image_paths
            
        except Exception as e:
            raise Exception(f"Errore conversione PDF: {str(e)}")
