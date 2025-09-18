"""
Module d'intégration du modèle YOLOv8 pour la détection de langage des signes
Projet créé par Marino ATOHOUN
"""

import os
import time
import random
from typing import List, Dict, Tuple
from PIL import Image
import json
from ultralytics import YOLO


class YOLOv8SignDetector:
    """
    Classe pour simuler l'intégration du modèle YOLOv8
    Dans un environnement réel, cette classe chargerait le fichier best.pt
    """
    
    def __init__(self, model_path: str = "/home/rinogeek/RINO/partition 1/all_project/signvision_project/translator/best.pt"):
        """
        Initialise le détecteur de signes
        
        Args:
            model_path: Chemin vers le fichier de modèle YOLOv8
        """
        self.model_path = model_path
        self.model_loaded = False
        self.sign_classes = [
            "bonjour", "merci", "au_revoir", "oui", "non", "s_il_vous_plait",
            "excusez_moi", "comment", "ou", "quand", "pourquoi", "qui",
            "eau", "manger", "boire", "dormir", "travail", "maison",
            "famille", "ami", "amour", "heureux", "triste", "colere",
            "peur", "surprise", "aide", "stop", "attention", "danger"
        ]
        self.load_model()
    
    def load_model(self):
        """Charge le modèle YOLOv8"""
        try:
            # Simulation du chargement du modèle
            # Dans un environnement réel, on utiliserait:
            # from ultralytics import YOLO
            print(f"Chargement du modèle depuis {self.model_path}...")
            self.model = YOLO(self.model_path)
            
            
            # time.sleep(1)  # Simulation du temps de chargement
            # self.model_loaded = True
            print("Modèle YOLOv8 chargé avec succès!")
            
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
            print("Utilisation du mode simulation...")
            self.model_loaded = False
    
    def detect_signs_image(self, image_path: str) -> List[Dict]:
        """
        Détecte les signes dans une image
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Liste des détections avec coordonnées et classes
        """
        if not self.model:
            raise Exception("Modèle non chargé")
        
        # Simulation de la détection
        # Dans un environnement réel:
        results = self.model(image_path)
        return self._process_results(results)
        
        #return self._simulate_detection(image_path)

    def _process_results(self, results) -> List[Dict]:
        """
        Transforme les résultats du modèle YOLOv8 en liste de détections au format attendu
        """
        detections = []
        # results.boxes.xyxy, results.boxes.conf, results.boxes.cls
        # On suppose que results est un objet ultralytics YOLO avec .boxes
        if hasattr(results, 'boxes'):
            boxes = results.boxes
            for i in range(len(boxes)):
                # Extraction des coordonnées et scores
                xyxy = boxes.xyxy[i].tolist() if hasattr(boxes.xyxy[i], 'tolist') else list(boxes.xyxy[i])
                conf = float(boxes.conf[i]) if hasattr(boxes.conf[i], 'item') else boxes.conf[i]
                cls_idx = int(boxes.cls[i]) if hasattr(boxes.cls[i], 'item') else boxes.cls[i]
                sign_class = self.sign_classes[cls_idx] if cls_idx < len(self.sign_classes) else str(cls_idx)
                detection = {
                    'class': sign_class,
                    'confidence': conf,
                    'bbox': {
                        'x': xyxy[0],
                        'y': xyxy[1],
                        'width': xyxy[2] - xyxy[0],
                        'height': xyxy[3] - xyxy[1]
                    },
                    'frame': 0
                }
                detections.append(detection)
        return detections
    
    def detect_signs_video(self, video_path: str) -> List[Dict]:
        """
        Détecte les signes dans une vidéo
        
        Args:
            video_path: Chemin vers la vidéo
            
        Returns:
            Liste des détections par frame
        """
        if not self.model:
            raise Exception("Modèle non chargé")
        
        # Simulation de la détection vidéo
        return self._simulate_video_detection(video_path)
    
    def _simulate_detection(self, file_path: str) -> List[Dict]:
        """Simule la détection de signes pour une image"""
        detections = []
        
        # Génère 1-3 détections aléatoirement
        num_detections = random.randint(1, 3)
        
        for i in range(num_detections):
            detection = {
                'class': random.choice(self.sign_classes),
                'confidence': round(random.uniform(0.6, 0.95), 3),
                'bbox': {
                    'x': random.randint(50, 300),
                    'y': random.randint(50, 200),
                    'width': random.randint(80, 150),
                    'height': random.randint(80, 150)
                },
                'frame': 0
            }
            detections.append(detection)
        
        return detections
    
    def _simulate_video_detection(self, video_path: str) -> List[Dict]:
        """Simule la détection de signes pour une vidéo"""
        detections = []
        
        # Simule 10-30 frames
        num_frames = random.randint(10, 30)
        
        for frame_num in range(num_frames):
            # Probabilité de détection par frame
            if random.random() > 0.3:  # 70% de chance de détection
                num_detections = random.randint(1, 2)
                
                for i in range(num_detections):
                    detection = {
                        'class': random.choice(self.sign_classes),
                        'confidence': round(random.uniform(0.5, 0.9), 3),
                        'bbox': {
                            'x': random.randint(50, 300),
                            'y': random.randint(50, 200),
                            'width': random.randint(80, 150),
                            'height': random.randint(80, 150)
                        },
                        'frame': frame_num
                    }
                    detections.append(detection)
        
        return detections
    
    def translate_signs_to_text(self, detections: List[Dict]) -> str:
        """
        Traduit les signes détectés en texte
        
        Args:
            detections: Liste des détections
            
        Returns:
            Texte traduit
        """
        if not detections:
            return "Aucun signe détecté"
        
        # Groupe les détections par frame et prend la plus confiante
        frame_signs = {}
        for detection in detections:
            frame = detection['frame']
            if frame not in frame_signs:
                frame_signs[frame] = []
            frame_signs[frame].append(detection)
        
        # Prend le signe le plus confiant par frame
        signs_sequence = []
        for frame in sorted(frame_signs.keys()):
            best_detection = max(frame_signs[frame], key=lambda x: x['confidence'])
            if best_detection['confidence'] > 0.6:  # Seuil de confiance
                signs_sequence.append(best_detection['class'])
        
        # Supprime les doublons consécutifs
        filtered_signs = []
        for sign in signs_sequence:
            if not filtered_signs or sign != filtered_signs[-1]:
                filtered_signs.append(sign)
        
        # Traduit en français
        translation_map = {
            "bonjour": "Bonjour",
            "merci": "Merci",
            "au_revoir": "Au revoir",
            "oui": "Oui",
            "non": "Non",
            "s_il_vous_plait": "S'il vous plaît",
            "excusez_moi": "Excusez-moi",
            "comment": "Comment",
            "ou": "Où",
            "quand": "Quand",
            "pourquoi": "Pourquoi",
            "qui": "Qui",
            "eau": "Eau",
            "manger": "Manger",
            "boire": "Boire",
            "dormir": "Dormir",
            "travail": "Travail",
            "maison": "Maison",
            "famille": "Famille",
            "ami": "Ami",
            "amour": "Amour",
            "heureux": "Heureux",
            "triste": "Triste",
            "colere": "Colère",
            "peur": "Peur",
            "surprise": "Surprise",
            "aide": "Aide",
            "stop": "Stop",
            "attention": "Attention",
            "danger": "Danger"
        }
        
        translated_words = [translation_map.get(sign, sign) for sign in filtered_signs]
        return " ".join(translated_words)
    
    def get_model_info(self) -> Dict:
        """Retourne les informations sur le modèle"""
        return {
            'model_path': self.model_path,
            'loaded': self.model,
            'classes_count': len(self.sign_classes),
            'classes': self.sign_classes
        }


# Instance globale du détecteur
detector = YOLOv8SignDetector()

