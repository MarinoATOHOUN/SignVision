"""
Vues Django pour SignVision AI
Projet créé par Marino ATOHOUN
"""

import os
import time
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import tempfile

from .models import UploadedFile, TranslationResult, SignDetection
from .ai_model import detector


def index(request):
    """Vue principale de l'application"""
    # Récupère le dernier résultat de traduction s'il existe
    latest_result = TranslationResult.objects.first()
    
    context = {
        'translation_result': latest_result,
    }
    
    return render(request, 'index.html', context)


@require_http_methods(["POST"])
def upload_file(request):
    """Gère l'upload et le traitement des fichiers"""
    try:
        if 'media_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Aucun fichier fourni'
            })
        
        uploaded_file = request.FILES['media_file']
        
        # Validation du type de fichier
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.avi', '.mov']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Type de fichier non supporté: {file_ext}'
            })
        
        # Détermine le type de fichier
        file_type = 'image' if file_ext in ['.jpg', '.jpeg', '.png'] else 'video'
        
        # Sauvegarde le fichier
        file_instance = UploadedFile.objects.create(
            file=uploaded_file,
            file_type=file_type,
            original_name=uploaded_file.name
        )
        
        # Traitement avec le modèle IA
        result_data = process_file_with_ai(file_instance)
        
        # Sauvegarde les résultats
        translation_result = TranslationResult.objects.create(
            uploaded_file=file_instance,
            detected_signs=result_data['detections'],
            translated_text=result_data['translated_text'],
            confidence_score=result_data['confidence_score'],
            processing_time=result_data['processing_time']
        )
        
        # Sauvegarde les détections individuelles
        for detection in result_data['detections']:
            SignDetection.objects.create(
                translation_result=translation_result,
                sign_class=detection['class'],
                confidence=detection['confidence'],
                bbox_x=detection['bbox']['x'],
                bbox_y=detection['bbox']['y'],
                bbox_width=detection['bbox']['width'],
                bbox_height=detection['bbox']['height'],
                frame_number=detection.get('frame', 0)
            )
        
        file_instance.processed = True
        file_instance.save()
        
        messages.success(request, f'Fichier {uploaded_file.name} traité avec succès!')
        
        return JsonResponse({
            'success': True,
            'data': {
                'translated_text': result_data['translated_text'],
                'confidence_score': result_data['confidence_score'],
                'processing_time': result_data['processing_time'],
                'detections': result_data['detections']
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du traitement: {str(e)}'
        })


@require_http_methods(["POST"])
def process_camera(request):
    """Traite les frames de la caméra en temps réel"""
    try:
        if 'camera_frame' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Aucune frame fournie'
            })
        
        camera_frame = request.FILES['camera_frame']
        
        # Sauvegarde temporaire de la frame
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            for chunk in camera_frame.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Traitement avec le modèle IA
            start_time = time.time()
            detections = detector.detect_signs_image(temp_file_path)
            translated_text = detector.translate_signs_to_text(detections)
            processing_time = time.time() - start_time
            
            # Calcul de la confiance moyenne
            confidence_score = 0
            if detections:
                confidence_score = sum(d['confidence'] for d in detections) / len(detections) * 100
            
            return JsonResponse({
                'success': True,
                'data': {
                    'translated_text': translated_text,
                    'confidence_score': round(confidence_score, 2),
                    'processing_time': round(processing_time, 2),
                    'detections': detections
                }
            })
            
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du traitement de la caméra: {str(e)}'
        })


@require_http_methods(["POST"])
def process_url(request):
    """Traite une vidéo depuis une URL"""
    try:
        video_url = request.POST.get('video_url', '').strip()
        
        if not video_url:
            return JsonResponse({
                'success': False,
                'error': 'URL de vidéo manquante'
            })
        
        # Validation basique de l'URL
        if not video_url.startswith(('http://', 'https://')):
            return JsonResponse({
                'success': False,
                'error': 'URL invalide'
            })
        
        # Simulation du téléchargement et traitement
        # Dans un environnement réel, on téléchargerait la vidéo
        start_time = time.time()
        
        # Simulation de détections pour une vidéo
        detections = detector.detect_signs_video(video_url)
        translated_text = detector.translate_signs_to_text(detections)
        processing_time = time.time() - start_time
        
        # Calcul de la confiance moyenne
        confidence_score = 0
        if detections:
            confidence_score = sum(d['confidence'] for d in detections) / len(detections) * 100
        
        return JsonResponse({
            'success': True,
            'data': {
                'translated_text': translated_text,
                'confidence_score': round(confidence_score, 2),
                'processing_time': round(processing_time, 2),
                'detections': detections[:10]  # Limite à 10 détections pour l'affichage
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du traitement de l\'URL: {str(e)}'
        })


def process_file_with_ai(file_instance):
    """
    Traite un fichier avec le modèle IA
    
    Args:
        file_instance: Instance du modèle UploadedFile
        
    Returns:
        dict: Résultats du traitement
    """
    start_time = time.time()
    
    file_path = file_instance.file.path
    
    try:
        if file_instance.file_type == 'image':
            detections = detector.detect_signs_image(file_path)
        else:  # video
            detections = detector.detect_signs_video(file_path)
        
        translated_text = detector.translate_signs_to_text(detections)
        processing_time = time.time() - start_time
        
        # Calcul de la confiance moyenne
        confidence_score = 0
        if detections:
            confidence_score = sum(d['confidence'] for d in detections) / len(detections) * 100
        
        return {
            'detections': detections,
            'translated_text': translated_text,
            'confidence_score': round(confidence_score, 2),
            'processing_time': round(processing_time, 2)
        }
        
    except Exception as e:
        return {
            'detections': [],
            'translated_text': f'Erreur lors du traitement: {str(e)}',
            'confidence_score': 0,
            'processing_time': time.time() - start_time
        }


def get_model_info(request):
    """Retourne les informations sur le modèle IA"""
    try:
        model_info = detector.get_model_info()
        return JsonResponse({
            'success': True,
            'data': model_info
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def get_recent_results(request):
    """Retourne les résultats récents de traduction"""
    try:
        results = TranslationResult.objects.select_related('uploaded_file')[:10]
        
        data = []
        for result in results:
            data.append({
                'id': result.id,
                'file_name': result.uploaded_file.original_name,
                'file_type': result.uploaded_file.file_type,
                'translated_text': result.translated_text,
                'confidence_score': result.confidence_score,
                'processing_time': result.processing_time,
                'created_at': result.created_at.isoformat(),
                'detections_count': result.detections.count()
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def about(request):
    """Page à propos"""
    context = {
        'developer': 'Marino ATOHOUN',
        'project_name': 'SignVision AI',
        'description': 'Application de détection et traduction du langage des signes utilisant YOLOv8'
    }
    return render(request, 'about.html', context)


def documentation(request):
    """Page de documentation"""
    return render(request, 'documentation.html')


def contact(request):
    """Page de contact"""
    return render(request, 'contact.html')
