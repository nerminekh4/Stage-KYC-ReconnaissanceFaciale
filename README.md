🧠 Détection comportementale de fraude KYC

Ce projet vise à renforcer la sécurité de l’onboarding client en automatisant le processus KYC (Know Your Customer) grâce à l’intelligence artificielle.
Il combine OCR, reconnaissance faciale et détection de vivacité afin de vérifier l’authenticité des documents d’identité et de prévenir la fraude..

🎯 Objectif

Capturer des signaux cognitifs et comportementaux pendant la saisie d’un formulaire
Simuler des profils réalistes (fraudeurs, hésitants, automatisés…)
Extraire des features interprétables
Entraîner un modèle XGBoost robuste
Déclencher des alertes en temps réel
🧠 Signaux comportementaux capturés

⏱️ Temps de focus par champ
🧭 Ordre de navigation
🖱️ Mouvements de souris, clics, scrolls
⌨️ Touches pressées (Tab, Enter, Delete)
📋 Copier/coller
🧠 Vitesse de remplissage et délai avant soumission
🛠️ Architecture technique

Composant	Description
formulaire.html	Formulaire KYC avec champs classiques et upload de justificatifs
tracking.js	Script de capture comportementale en temps réel
app.py	Backend Flask avec endpoints /api/save et /api/predict
feature_extractor.py	Extraction de features interprétables à partir des signaux bruts
database.py	Base SQLite avec tables sessions, fields, clicks, mouse_movements
generate_cases.py	Générateur de profils cognitifs simulés (10 types de comportements)
build_training_dataset.py	Fusion des features extraites avec les labels métier pour créer le dataset d'entraînement
train_xgboost.py	Entraînement du modèle XGBoost + validation croisée + interprétabilité
kyc_fraud_demo.py	Interface Streamlit pour tester le modèle et visualiser les prédictions
