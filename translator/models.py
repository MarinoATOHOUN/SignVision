"""
Modèles Django pour SignVision AI
Projet créé par Marino ATOHOUN
"""

from django.db import models
from django.utils import timezone
import os


def upload_to(instance, filename):
    """Fonction pour définir le chemin d'upload des fichiers"""
    ext = filename.split('.')[-1]
    filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('uploads', filename)


class UploadedFile(models.Model):
    """Modèle pour stocker les fichiers uploadés"""
    
    FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
    ]
    
    file = models.FileField(upload_to=upload_to)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.original_name} ({self.file_type})"


class TranslationResult(models.Model):
    """Modèle pour stocker les résultats de traduction"""
    
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='translations')
    detected_signs = models.JSONField(default=list)  # Liste des signes détectés
    translated_text = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    processing_time = models.FloatField(default=0.0)  # Temps de traitement en secondes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Traduction pour {self.uploaded_file.original_name}"


class SignDetection(models.Model):
    """Modèle pour stocker les détections individuelles de signes"""
    
    translation_result = models.ForeignKey(TranslationResult, on_delete=models.CASCADE, related_name='detections')
    sign_class = models.CharField(max_length=100)  # Classe du signe détecté
    confidence = models.FloatField()  # Confiance de la détection
    bbox_x = models.FloatField()  # Coordonnées de la bounding box
    bbox_y = models.FloatField()
    bbox_width = models.FloatField()
    bbox_height = models.FloatField()
    frame_number = models.IntegerField(default=0)  # Numéro de frame pour les vidéos
    
    class Meta:
        ordering = ['frame_number', '-confidence']
    
    def __str__(self):
        return f"{self.sign_class} ({self.confidence:.2f})"
