# Application KYC avec Validation de Pièces d'Identité

## Problème résolu

L'application KYC utilisait Face++ pour comparer un selfie avec une image uploadée, mais **ne validait pas si l'image était réellement une pièce d'identité officielle**. Les utilisateurs pouvaient uploader n'importe quelle photo.

## Solution implémentée

### 1. **Validation automatique des documents**
- **Détection IA** : Utilise GPT-4 Vision ou OCR local pour identifier les pièces d'identité officielles
- **Types supportés** : Carte d'identité, passeport, permis de conduire français
- **Extraction de données** : Nom, prénom, date de naissance, numéro d'identité

### 2. **Système hybride**
- **Méthode principale** : OpenAI GPT-4 Vision (haute précision)
- **Fallback** : API Python avec EasyOCR (fonctionne hors ligne)
- **Basculement automatique** en cas d'erreur

### 3. **Interface utilisateur améliorée**
- **Feedback en temps réel** sur la validation
- **Auto-remplissage** des champs détectés
- **Vérification de cohérence** entre données saisies et extraites
- **Messages d'erreur** explicites

## Architecture

```
frontend-kyc/                 # Application Angular
├── src/app/
│   ├── components/
│   │   ├── kyc-form/         # Formulaire principal avec validation
│   │   └── facial-verification/ # Composant selfie
│   └── services/
│       └── document-validation.service.ts # Service de validation

backend/                      # API Python pour OCR
├── document_validation_api.py # Serveur Flask avec EasyOCR
├── requirements.txt          # Dépendances Python
└── n8n-workflow.json        # Workflow existant
```

## Installation et Configuration

### 1. **Backend Python (OCR)**
```bash
cd backend
pip install -r requirements.txt
python document_validation_api.py
```

### 2. **Frontend Angular**
```bash
cd frontend-kyc
npm install
ng serve
```

### 3. **Configuration**
Dans `src/environments/environment.ts` :
```typescript
export const environment = {
  openaiApiKey: 'sk-your-openai-api-key', // Optionnel
  documentValidationApiUrl: 'http://localhost:5000/api/validate-document-ocr',
  n8nWebhookUrl: 'http://localhost:5678/webhook-test/kyc-verification'
};
```

## Fonctionnalités ajoutées

### **Validation de documents**
- ✅ Détection automatique du type de document
- ✅ Vérification de l'authenticité (éléments de sécurité)
- ✅ Score de confiance (0-100%)
- ✅ Extraction OCR des données personnelles

### **Auto-remplissage intelligent**
- ✅ Remplissage automatique des champs détectés
- ✅ Option pour activer/désactiver l'auto-remplissage
- ✅ Vérification de cohérence des données

### **Gestion d'erreurs robuste**
- ✅ Validation avant comparaison faciale
- ✅ Messages d'erreur explicites
- ✅ Fallback automatique entre méthodes

## Workflow de validation

1. **Upload d'image** → Validation automatique du document
2. **Extraction de données** → Auto-remplissage optionnel
3. **Vérification de cohérence** → Comparaison données saisies/extraites
4. **Validation du formulaire** → Vérification complète
5. **Prise de selfie** → Comparaison faciale avec Face++
6. **Envoi à n8n** → Traitement final

## API Endpoints

### Backend Python
- `POST /api/validate-document-ocr` - Validation avec OCR
- `GET /api/health` - Vérification de santé

### Méthodes de validation
- **OpenAI GPT-4 Vision** : Haute précision, nécessite clé API
- **EasyOCR local** : Fonctionne hors ligne, gratuit

## Types de documents supportés

- **Carte d'identité française** 🆔
- **Passeport français** 📘  
- **Permis de conduire** 🚗

## Améliorations de sécurité

- **Validation obligatoire** : Impossible de continuer sans document valide
- **Détection de faux documents** : Vérification des éléments de sécurité
- **Cohérence des données** : Comparaison automatique des informations
- **Logs de sécurité** : Traçabilité des tentatives de validation

## Utilisation

1. **Remplir le formulaire** avec les informations personnelles
2. **Uploader une pièce d'identité** → Validation automatique
3. **Vérifier les données extraites** (auto-remplissage)
4. **Cliquer "Envoyer"** → Prise de selfie
5. **Validation finale** → Comparaison faciale + envoi n8n

## Dépendances principales

### Frontend
- Angular 17+
- HttpClient pour les appels API
- FormsModule pour les formulaires

### Backend  
- Flask (serveur web)
- EasyOCR (reconnaissance de texte)
- OpenCV (traitement d'image)
- NumPy (calculs matriciels)

## Sécurité

- **Clé API OpenAI** : Stockée dans environment.ts (à sécuriser en production)
- **CORS configuré** : Accès contrôlé depuis le frontend
- **Validation côté serveur** : Double vérification backend
- **Logs de sécurité** : Traçabilité des actions

---

**Résultat** : L'application peut maintenant différencier une vraie pièce d'identité d'une photo quelconque, avec extraction automatique des données et vérification de cohérence. 🎯
