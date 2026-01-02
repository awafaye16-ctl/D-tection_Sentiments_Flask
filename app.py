"""
Application Flask pour l'analyse de sentiments
"""
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import logging

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importation de notre package
try:
    from src.sentiment_analyzer import analyze_sentiment
    from src.utils import format_sentiment_result, validate_text
    PACKAGE_LOADED = True
    logger.info("✅ Package sentiment_analysis chargé avec succès")
except ImportError as e:
    PACKAGE_LOADED = False
    logger.error(f"❌ Erreur chargement package: {e}")

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Variables d'environnement Watson
WATSON_API_KEY = os.getenv('WATSON_API_KEY')
WATSON_URL = os.getenv('WATSON_URL')

# Vérification de la configuration
if not WATSON_API_KEY or not WATSON_URL:
    logger.warning("⚠️  Variables d'environnement Watson non configurées")
    logger.warning("   Utilisation du mode démo (résultats simulés)")

### ROUTES DE L'APPLICATION ###

@app.route('/')
def home():
    """
    Page d'accueil - Interface web
    """
    logger.info("Accès page d'accueil")
    return render_template(
        'index.html',
        app_name="Analyseur de Sentiments",
        package_loaded=PACKAGE_LOADED,
        watson_configured=bool(WATSON_API_KEY and WATSON_URL)
    )

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint API pour l'analyse de sentiments
    """
    logger.info("Requête d'analyse reçue")
    
    # Récupération du texte
    data = request.get_json()
    if not data or 'text' not in data:
        logger.warning("Requête sans texte")
        return jsonify({
            'error': 'Texte manquant',
            'message': 'Veuillez fournir un texte à analyser.'
        }), 400
    
    text = data['text']
    
    # Validation du texte
    validation = validate_text(text)
    if not validation['valid']:
        logger.warning(f"Texte invalide: {validation['message']}")
        return jsonify({
            'error': 'Texte invalide',
            'message': validation['message']
        }), 400
    
    logger.info(f"Analyse de texte ({len(text)} caractères)")
    
    try:
        # Analyse du sentiment
        if WATSON_API_KEY and WATSON_URL:
            # Mode réel avec Watson
            result = analyze_sentiment(text, WATSON_API_KEY, WATSON_URL)
            result['mode'] = 'watson'
        else:
            # Mode démo (simulation)
            result = demo_sentiment_analysis(text)
            result['mode'] = 'demo'
            result['warning'] = 'Mode démo - résultats simulés'
        
        # Formatage pour l'affichage
        formatted_result = format_sentiment_result(result)
        
        # Log du résultat
        sentiment = formatted_result.get('sentiment_fr', 'Inconnu')
        logger.info(f"Résultat: {sentiment} (score: {result.get('score', 0):.3f})")
        
        return jsonify(formatted_result)
        
    except Exception as e:
        logger.exception(f"Erreur lors de l'analyse: {e}")
        return jsonify({
            'error': 'Erreur interne',
            'message': 'Une erreur est survenue lors de l\'analyse.',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/health')
def health_check():
    """
    Endpoint de vérification de santé
    """
    health_status = {
        'status': 'healthy',
        'version': '1.0.0',
        'package_loaded': PACKAGE_LOADED,
        'watson_configured': bool(WATSON_API_KEY and WATSON_URL),
        'endpoints': ['/', '/analyze', '/health']
    }
    return jsonify(health_status)

### FONCTION DÉMO ###

def demo_sentiment_analysis(text: str) -> dict:
    """
    Analyse de sentiments simulée pour le mode démo
    
    Args:
        text: Texte à analyser
        
    Returns:
        Résultat simulé
    """
    # Mots-clés pour déterminer le sentiment
    positive_words = ['bon', 'bonne', 'excellent', 'super', 'génial', 'heureux',
                     'content', 'parfait', 'magnifique', 'fantastique']
    negative_words = ['mauvais', 'mauvaise', 'terrible', 'horrible', 'nul',
                     'triste', 'déçu', 'déçue', 'problème', 'erreur']
    
    text_lower = text.lower()
    
    # Comptage des mots positifs/négatifs
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calcul du score
    total_words = len(text.split())
    if total_words > 0:
        score = (positive_count - negative_count) / total_words
    else:
        score = 0.0
    
    # Limitation du score
    score = max(-1.0, min(1.0, score))
    
    # Détermination du sentiment
    if score > 0.2:
        sentiment = 'POSITIVE'
        label = '😊 Positif (démo)'
    elif score < -0.2:
        sentiment = 'NEGATIVE'
        label = '😞 Négatif (démo)'
    else:
        sentiment = 'NEUTRAL'
        label = '😐 Neutre (démo)'
    
    return {
        'sentiment': sentiment,
        'score': score,
        'label': label,
        'confidence': min(0.95, abs(score) + 0.3),
        'demo': True
    }

### GESTIONNAIRES D'ERREURS ###

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Page non trouvée: {request.path}")
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Endpoint non trouvé',
            'message': f'L\'endpoint {request.path} n\'existe pas.'
        }), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("Erreur interne du serveur")
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Erreur interne',
            'message': 'Une erreur est survenue sur le serveur.'
        }), 500
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(error):
    logger.warning("Fichier trop volumineux")
    return jsonify({
        'error': 'Fichier trop volumineux',
        'message': 'Le fichier dépasse la taille maximale autorisée.'
    }), 413

### POINT D'ENTRÉE ###

if __name__ == '__main__':
    """
    Point d'entrée principal
    """
    print("\n" + "="*60)
    print("🚀 APPLICATION D'ANALYSE DE SENTIMENTS")
    print("="*60)
    print(f"📦 Package: {'✅ Chargé' if PACKAGE_LOADED else '❌ Absent'}")
    print(f"🤖 Watson AI: {'✅ Configuré' if WATSON_API_KEY and WATSON_URL else '⚠️  Mode démo'}")
    print(f"🌐 Serveur: http://localhost:5000")
    print(f"📊 Endpoints:")
    print(f"   - /              : Interface web")
    print(f"   - /analyze       : API d'analyse")
    print(f"   - /health        : Vérification santé")
    print("="*60 + "\n")
    
    # Démarrage du serveur
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )