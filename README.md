# SignVision AI - Détection de Langage des Signes

**Projet créé par Marino ATOHOUN**

## Description

SignVision AI est une application web Django avancée pour la détection et la traduction du langage des signes en temps réel. L'application utilise un modèle YOLOv8 pour détecter les signes dans les images et vidéos, puis les traduit en texte français.

## Fonctionnalités

### 🎥 Sources d'entrée multiples
- **Caméra en direct** : Détection en temps réel via la webcam
- **Upload de fichiers** : Support des images (JPG, PNG) et vidéos (MP4, AVI, MOV)
- **URL de vidéo** : Traitement de vidéos depuis des URLs

### 🤖 Intelligence Artificielle
- Modèle YOLOv8 intégré pour la détection de signes
- Plus de 30 classes de signes supportées
- Traduction automatique en français
- Calcul de confiance et temps de traitement

### 🎨 Interface utilisateur
- Design moderne avec Tailwind CSS
- Interface responsive (mobile et desktop)
- Animations et transitions fluides
- Affichage en temps réel des résultats

### 📊 Fonctionnalités avancées
- Sauvegarde des résultats en base de données
- Historique des traitements
- API REST pour l'intégration
- Gestion des erreurs robuste

## Classes de signes supportées

L'application peut détecter et traduire les signes suivants :

**Salutations et politesse :**
- Bonjour, Merci, Au revoir, S'il vous plaît, Excusez-moi

**Questions :**
- Comment, Où, Quand, Pourquoi, Qui

**Réponses :**
- Oui, Non

**Actions quotidiennes :**
- Eau, Manger, Boire, Dormir, Travail

**Relations :**
- Maison, Famille, Ami, Amour

**Émotions :**
- Heureux, Triste, Colère, Peur, Surprise

**Sécurité :**
- Aide, Stop, Attention, Danger

## Installation et utilisation

### Prérequis
- Python 3.8+
- Django 3.2+
- Pillow pour le traitement d'images

### Installation

1. **Extraire l'archive**
```bash
unzip signvision_ai_marino_atohoun.zip
cd signvision_project
```

2. **Installer les dépendances**
```bash
pip install django pillow
```

3. **Appliquer les migrations**
```bash
python manage.py migrate
```

4. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

6. **Accéder à l'application**
Ouvrir http://localhost:8000 dans votre navigateur

### Utilisation

#### Mode Caméra
1. Cliquer sur "Activer la caméra"
2. Autoriser l'accès à la webcam
3. Activer le "Mode temps réel" pour la détection continue
4. Les résultats s'affichent automatiquement

#### Upload de fichiers
1. Glisser-déposer un fichier ou cliquer pour sélectionner
2. Le traitement démarre automatiquement
3. Les résultats s'affichent avec les détections et la traduction

#### URL de vidéo
1. Saisir l'URL d'une vidéo
2. Cliquer sur le bouton de téléchargement
3. Attendre le traitement et voir les résultats

## Structure du projet

```
signvision_project/
├── manage.py                 # Script de gestion Django
├── signvision/              # Configuration principale
│   ├── settings.py          # Paramètres Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuration WSGI
├── translator/              # Application principale
│   ├── models.py           # Modèles de données
│   ├── views.py            # Vues et logique métier
│   ├── urls.py             # URLs de l'application
│   ├── ai_model.py         # Intégration YOLOv8
│   └── migrations/         # Migrations de base de données
├── templates/               # Templates HTML
│   ├── base.html           # Template de base
│   └── index.html          # Page principale
├── static/                  # Fichiers statiques
│   ├── css/style.css       # Styles personnalisés
│   └── js/main.js          # JavaScript principal
├── media/                   # Fichiers uploadés
└── README.md               # Documentation
```

## API REST

L'application expose plusieurs endpoints API :

- `POST /upload/` - Upload et traitement de fichiers
- `POST /process_camera/` - Traitement des frames de caméra
- `POST /process_url/` - Traitement d'URLs de vidéo
- `GET /api/model_info/` - Informations sur le modèle
- `GET /api/recent_results/` - Résultats récents

## Modèle IA

### Intégration YOLOv8
Le projet est conçu pour utiliser un modèle YOLOv8 personnalisé (`best.pt`). En l'absence du fichier de modèle, l'application fonctionne en mode simulation avec des détections aléatoirement générées pour démonstration.

### Remplacement du modèle
Pour utiliser votre propre modèle YOLOv8 :
1. Placer le fichier `best.pt` dans le répertoire racine
2. Le modèle sera automatiquement chargé au démarrage

## Technologies utilisées

- **Backend** : Django 3.2, Python 3.8+
- **Frontend** : HTML5, CSS3, JavaScript ES6, Tailwind CSS
- **IA** : YOLOv8 (simulation), Pillow
- **Base de données** : SQLite (développement)
- **Icons** : Font Awesome 6.4

## Sécurité

- Protection CSRF activée
- Validation des types de fichiers
- Limitation de taille des uploads (50MB)
- Nettoyage automatique des fichiers temporaires

## Performance

- Traitement optimisé des images et vidéos
- Cache des résultats en base de données
- Interface responsive et animations fluides
- Gestion d'erreurs robuste

## Développement

### Personnalisation
- Modifier `translator/ai_model.py` pour intégrer votre modèle
- Adapter `static/css/style.css` pour le design
- Étendre `translator/models.py` pour de nouvelles fonctionnalités

### Tests
```bash
python manage.py test
```

### Administration
Créer un superutilisateur pour accéder à l'admin Django :
```bash
python manage.py createsuperuser
```

## Licence

Ce projet est développé par **Marino ATOHOUN** dans le cadre d'un projet d'IA de traduction du langage des signes.

## Contact

Pour toute question ou suggestion concernant ce projet, veuillez contacter Marino ATOHOUN.

---

**SignVision AI** - Rendant la communication accessible à tous grâce à l'intelligence artificielle.

