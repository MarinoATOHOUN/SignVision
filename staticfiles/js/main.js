/*
SignVision AI - JavaScript principal
Projet créé par Marino ATOHOUN
*/

// Variables globales
let currentStream = null;
let isProcessing = false;
let detectionInterval = null;

// DOM Elements
const startCameraBtn = document.getElementById('startCamera');
const stopCameraBtn = document.getElementById('stopCamera');
const liveCamera = document.getElementById('liveCamera');
const cameraCanvas = document.getElementById('cameraCanvas');
const cameraContainer = document.getElementById('cameraContainer');
const mediaUpload = document.getElementById('mediaUpload');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const videoUrl = document.getElementById('videoUrl');
const loadUrlBtn = document.getElementById('loadUrl');
const processedVideo = document.getElementById('processedVideo');
const outputCanvas = document.getElementById('outputCanvas');
const translationResult = document.getElementById('translationResult');
const processingStatus = document.getElementById('processingStatus');
const copyResultsBtn = document.getElementById('copyResults');
const startProcessingBtn = document.getElementById('startProcessing');
const stopProcessingBtn = document.getElementById('stopProcessing');
const realTimeMode = document.getElementById('realTimeMode');
const showLandmarks = document.getElementById('showLandmarks');
const uploadForm = document.getElementById('uploadForm');

// Fonctions utilitaires
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateStatus(message, type = 'info') {
    processingStatus.textContent = message;
    processingStatus.className = `text-sm ${type === 'error' ? 'text-red-500' : type === 'success' ? 'text-green-500' : 'text-gray-500'}`;
}

function showLoading(button) {
    button.classList.add('loading');
    button.disabled = true;
}

function hideLoading(button) {
    button.classList.remove('loading');
    button.disabled = false;
}

// Fonctions de caméra
async function startCamera() {
    try {
        showLoading(startCameraBtn);
        updateStatus("Activation de la caméra...");
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        currentStream = stream;
        liveCamera.srcObject = stream;
        liveCamera.classList.remove('hidden');
        cameraContainer.querySelector('.fa-camera').parentElement.classList.add('hidden');
        
        startCameraBtn.disabled = true;
        stopCameraBtn.disabled = false;
        hideLoading(startCameraBtn);
        
        updateStatus("Caméra activée - Prêt à traiter", 'success');
        
        // Démarrer la détection en temps réel si activée
        if (realTimeMode.checked) {
            startRealTimeDetection();
        }
        
    } catch (err) {
        console.error("Erreur d'accès à la caméra:", err);
        updateStatus("Erreur: Accès à la caméra refusé", 'error');
        hideLoading(startCameraBtn);
    }
}

function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
        liveCamera.srcObject = null;
        liveCamera.classList.add('hidden');
        cameraContainer.querySelector('.fa-camera').parentElement.classList.remove('hidden');
        
        startCameraBtn.disabled = false;
        stopCameraBtn.disabled = true;
        
        stopRealTimeDetection();
        updateStatus("Caméra désactivée");
    }
}

function startRealTimeDetection() {
    if (detectionInterval) return;
    
    detectionInterval = setInterval(() => {
        if (liveCamera.videoWidth > 0 && liveCamera.videoHeight > 0) {
            captureAndProcess();
        }
    }, 2000); // Traitement toutes les 2 secondes
}

function stopRealTimeDetection() {
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
}

async function captureAndProcess() {
    if (!liveCamera.srcObject || isProcessing) return;
    
    try {
        // Capture de l'image depuis la caméra
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = liveCamera.videoWidth;
        canvas.height = liveCamera.videoHeight;
        ctx.drawImage(liveCamera, 0, 0);
        
        // Conversion en blob
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('camera_frame', blob, 'camera_frame.jpg');
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            
            try {
                const response = await fetch('/process_camera/', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.success) {
                    displayResults(result.data);
                }
            } catch (error) {
                console.error('Erreur lors du traitement:', error);
            }
        }, 'image/jpeg', 0.8);
        
    } catch (error) {
        console.error('Erreur lors de la capture:', error);
    }
}

// Gestion de l'upload de fichiers
function handleFileUpload() {
    const file = mediaUpload.files[0];
    if (!file) return;
    
    fileName.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
    fileInfo.classList.remove('hidden');
    
    updateStatus(`Fichier chargé: ${file.name}`, 'success');
    startProcessingBtn.disabled = false;
    
    // Upload automatique du fichier
    uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('media_file', file);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    
    try {
        showLoading(startProcessingBtn);
        updateStatus("Upload et traitement en cours...");
        
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.data);
            updateStatus("Traitement terminé avec succès", 'success');
        } else {
            updateStatus(`Erreur: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Erreur lors de l\'upload:', error);
        updateStatus("Erreur lors de l'upload", 'error');
    } finally {
        hideLoading(startProcessingBtn);
    }
}

// Gestion de l'URL de vidéo
async function loadVideoFromUrl() {
    const url = videoUrl.value.trim();
    if (!url) {
        updateStatus("Veuillez entrer une URL valide", 'error');
        return;
    }
    
    try {
        showLoading(loadUrlBtn);
        updateStatus(`Chargement de la vidéo depuis ${url}...`);
        
        const formData = new FormData();
        formData.append('video_url', url);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        const response = await fetch('/process_url/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.data);
            updateStatus("Vidéo chargée et traitée avec succès", 'success');
            startProcessingBtn.disabled = false;
        } else {
            updateStatus(`Erreur: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Erreur lors du chargement:', error);
        updateStatus("Erreur lors du chargement de la vidéo", 'error');
    } finally {
        hideLoading(loadUrlBtn);
    }
}

// Affichage des résultats
function displayResults(data) {
    if (!data) return;
    
    const resultDiv = translationResult;
    
    if (data.translated_text) {
        resultDiv.innerHTML = `
            <div class="fade-in">
                <p class="text-lg font-medium text-gray-800 mb-3">${data.translated_text}</p>
                <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div class="stat-card">
                        <div class="stat-number">${data.confidence_score || 0}%</div>
                        <div class="stat-label">Confiance</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.processing_time || 0}s</div>
                        <div class="stat-label">Temps</div>
                    </div>
                </div>
                ${data.detections ? `
                    <div class="mt-4">
                        <h4 class="font-medium text-gray-700 mb-2">Signes détectés:</h4>
                        <div class="space-y-2">
                            ${data.detections.map(detection => `
                                <div class="detection-box">
                                    <div class="flex justify-between items-center">
                                        <span class="font-medium">${detection.class}</span>
                                        <span class="text-sm">${(detection.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                    <div class="confidence-bar mt-1">
                                        <div class="confidence-fill" style="width: ${detection.confidence * 100}%"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        copyResultsBtn.disabled = false;
    } else {
        resultDiv.innerHTML = `
            <div class="text-center text-gray-400 py-8">
                <i class="fas fa-exclamation-triangle text-3xl mb-2"></i>
                <p>Aucun signe détecté dans le média</p>
            </div>
        `;
    }
}

// Contrôles de traitement
function startProcessing() {
    if (currentStream && realTimeMode.checked) {
        startRealTimeDetection();
        updateStatus("Détection en temps réel activée", 'success');
    } else {
        updateStatus("Sélectionnez un fichier ou activez la caméra", 'error');
    }
    
    startProcessingBtn.disabled = true;
    stopProcessingBtn.disabled = false;
    isProcessing = true;
}

function stopProcessing() {
    stopRealTimeDetection();
    updateStatus("Traitement arrêté");
    
    startProcessingBtn.disabled = false;
    stopProcessingBtn.disabled = true;
    isProcessing = false;
}

// Copie des résultats
function copyResults() {
    const text = translationResult.textContent.trim();
    if (text) {
        navigator.clipboard.writeText(text).then(() => {
            updateStatus("Résultats copiés dans le presse-papiers", 'success');
        }).catch(() => {
            updateStatus("Erreur lors de la copie", 'error');
        });
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Caméra
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);
    
    // Upload de fichiers
    mediaUpload.addEventListener('change', handleFileUpload);
    
    // URL de vidéo
    loadUrlBtn.addEventListener('click', loadVideoFromUrl);
    
    // Contrôles
    startProcessingBtn.addEventListener('click', startProcessing);
    stopProcessingBtn.addEventListener('click', stopProcessing);
    copyResultsBtn.addEventListener('click', copyResults);
    
    // Mode temps réel
    realTimeMode.addEventListener('change', function() {
        if (currentStream) {
            if (this.checked && isProcessing) {
                startRealTimeDetection();
            } else {
                stopRealTimeDetection();
            }
        }
    });
    
    // Drag & Drop
    const uploadArea = document.querySelector('.file-upload-label');
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('bg-blue-200');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('bg-blue-200');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('bg-blue-200');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            mediaUpload.files = files;
            handleFileUpload();
        }
    });
    
    updateStatus("Application prête");
});

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    updateStatus("Une erreur inattendue s'est produite", 'error');
});

// Nettoyage lors de la fermeture de la page
window.addEventListener('beforeunload', function() {
    if (currentStream) {
        stopCamera();
    }
    stopRealTimeDetection();
});

