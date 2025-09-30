from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import easyocr
import numpy as np
import base64
import re
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:4200', 'http://127.0.0.1:4200'], 
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reader = easyocr.Reader(['fr', 'en'])

class DocumentValidator:
    def __init__(self):
        self.id_patterns = {
            'carte_identite': [
                r'RÉPUBLIQUE\s+FRANÇAISE',
                r'CARTE\s+NATIONALE\s+D\'IDENTITÉ',
                r'CARTE\s+D\'IDENTITÉ',
                r'PRÉFECTURE',
                r'VALABLE\s+JUSQU\'AU'
            ],
            'passeport': [
                r'PASSEPORT',
                r'PASSPORT', 
                r'RÉPUBLIQUE\s+FRANÇAISE',
                r'REPUBLIQUE\s+FRANCAISE',
                r'RÉPUBLIQUE\s+TUNISIENNE',
                r'REPUBLIQUE\s+TUNISIENNE',
                r'TUNISIAN\s+REPUBLIC',
                r'REPUBLIC\s+OF\s+TUNISIA',
                r'TYPE\s*P',
                r'FRANCE',
                r'TUNISIA',
                r'TUNISIE',
                r'FRENCH\s+REPUBLIC',
                r'P<FRA',
                r'P<TUN',
                r'FRANÇAIS',
                r'FRANCAIS',
                r'TUNISIAN',
                r'TUN',
                r'SPECIMEN',
                r'SPÉCIMEN',
                r'P<',
                r'[A-Z]{2}[A-Z0-9]{6,9}',  # Pattern pour numéros de passeport
                r'\d{2}\s*\d{2}\s*\d{4}',  # Pattern pour dates
                r'M\s*[A-Z]',  # Pattern pour sexe masculin
                r'F\s*[A-Z]'   # Pattern pour sexe féminin
            ],
            'permis_conduire': [
                r'PERMIS\s+DE\s+CONDUIRE',
                r'DRIVING\s+LICENCE',
                r'RÉPUBLIQUE\s+FRANÇAISE',
                r'PRÉFECTURE'
            ]
        }
        
        self.data_patterns = {
            'nom': r'(?:NOM|SURNAME|NAME|اللقب)\s*:?\s*([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸ\s\-\']+)',
            'prenom': r'(?:PRÉNOM|PRENOM|GIVEN\s+NAME|FIRST\s+NAME|الاسم)\s*:?\s*([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞÿa-z\s\-\']+)',
            'date_naissance': r'(?:NÉ\s+LE|NEE?\s+LE|DATE\s+OF\s+BIRTH|BIRTH|تاريخ\s+الولادة)\s*:?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{4})',
            'numero_id': r'(?:N°|NO|NUM|NUMERO|رقم)\s*:?\s*([A-Z0-9]{8,15})'
        }

    def decode_base64_image(self, base64_string):
        try:
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            img_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
        except Exception as e:
            logger.error(f"Erreur décodage image: {e}")
            return None

    def preprocess_image(self, image):
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            try:
                denoised = cv2.fastNlMeansDenoising(enhanced)
                return denoised
            except Exception:
                return enhanced
                
        except Exception as e:
            logger.error(f"Erreur prétraitement: {e}")
            return image

    def extract_text_with_ocr(self, image):
        try:
            processed_image = self.preprocess_image(image)
            
            results = reader.readtext(processed_image)
            
            full_text = ' '.join([result[1] for result in results])
            
            return full_text, results
        except Exception as e:
            logger.error(f"Erreur OCR: {e}")
            return "", []

    def detect_document_type(self, text):
        text_upper = text.upper()
        logger.info(f"🔍 Recherche de patterns dans: {text_upper[:100]}...")
        
        for doc_type, patterns in self.id_patterns.items():
            matches = 0
            matched_patterns = []
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    matches += 1
                    matched_patterns.append(pattern)
            
            logger.info(f"📊 {doc_type}: {matches}/{len(patterns)} patterns trouvés: {matched_patterns}")
            
         
            if doc_type == 'passeport' and matches >= 1:
                return doc_type, max((matches / len(patterns)) * 100, 25)  
            elif matches >= 2:
                return doc_type, (matches / len(patterns)) * 100
        
        return 'inconnu', 0

    def extract_personal_data(self, text):
        extracted_data = {}
        
        for field, pattern in self.data_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                
                if field == 'date_naissance':
                    value = self.normalize_date(value)
                elif field in ['nom', 'prenom']:
                    value = self.normalize_name(value)
                elif field == 'numero_id':
                    value = re.sub(r'\s+', '', value) 
                
                extracted_data[field] = value
        
        return extracted_data

    def normalize_date(self, date_str):
        try:
            formats = ['%d/%m/%Y', '%d.%m.%Y', '%d-%m-%Y', '%d %m %Y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str 
        except:
            return date_str

    def normalize_name(self, name):
        name = re.sub(r'[^\w\s\-\'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', '', name, flags=re.IGNORECASE)
        name = ' '.join(name.split())  # Normaliser espaces
        return name.title()  # Première lettre en majuscule

    def validate_document(self, base64_image):
        try:
            image = self.decode_base64_image(base64_image)
            if image is None:
                return {
                    'isValidDocument': False,
                    'documentType': 'erreur',
                    'confidence': 0,
                    'errors': ['Impossible de décoder l\'image']
                }

            full_text, ocr_results = self.extract_text_with_ocr(image)
            
            if not full_text.strip():
                return {
                    'isValidDocument': False,
                    'documentType': 'illisible',
                    'confidence': 0,
                    'errors': ['Aucun texte détecté dans l\'image']
                }

            doc_type, confidence = self.detect_document_type(full_text)
            logger.info(f"📋 Texte extrait: {full_text[:200]}...")
            logger.info(f"🔍 Type détecté: {doc_type}, Confiance: {confidence}%")
            
            extracted_data = self.extract_personal_data(full_text)

            is_valid = doc_type != 'inconnu' and confidence > 20
            
            errors = []
            if not is_valid:
                if doc_type == 'inconnu':
                    errors.append('Type de document non reconnu')
                if confidence <= 20:
                    errors.append('Confiance trop faible dans la détection')
            
            if extracted_data:
                confidence += min(len(extracted_data) * 10, 30)
                confidence = min(confidence, 100)

            return {
                'isValidDocument': is_valid,
                'documentType': doc_type,
                'confidence': round(confidence, 1),
                'extractedData': extracted_data if extracted_data else None,
                'errors': errors if errors else None,
                'debugInfo': {
                    'textLength': len(full_text),
                    'ocrResults': len(ocr_results)
                }
            }

        except Exception as e:
            logger.error(f"Erreur validation document: {e}")
            return {
                'isValidDocument': False,
                'documentType': 'erreur',
                'confidence': 0,
                'errors': [f'Erreur interne: {str(e)}']
            }

validator = DocumentValidator()

@app.route('/api/validate-document-ocr', methods=['POST', 'OPTIONS'])
def validate_document_ocr():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'error': 'Image base64 requise dans le champ "image"'
            }), 400

        result = validator.validate_document(data['image'])
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        logger.error(f"Erreur endpoint: {e}")
        response = jsonify({
            'error': f'Erreur serveur: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'service': 'Document Validation API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Démarrage du serveur de validation de documents...")
    print("📋 Endpoints disponibles:")
    print("   POST /api/validate-document-ocr - Validation de documents")
    print("   GET  /api/health - Vérification de santé")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
