"""
Utilitaires de formatage pour l'application
"""

def format_sentiment_result(result: dict) -> dict:
    """
    Formate les résultats pour l'affichage web
    
    Args:
        result: Résultat brut de l'analyseur
        
    Returns:
        Résultat formaté pour l'affichage
    """
    # Copie du résultat pour ne pas modifier l'original
    formatted = result.copy()
    
    # Ajout de classes CSS basées sur le sentiment
    sentiment_classes = {
        'POSITIVE': 'sentiment-positive',
        'NEGATIVE': 'sentiment-negative', 
        'NEUTRAL': 'sentiment-neutral',
        'ERROR': 'sentiment-error'
    }
    
    formatted['css_class'] = sentiment_classes.get(
        result.get('sentiment', 'NEUTRAL'), 
        'sentiment-neutral'
    )
    
    # Formatage du score en pourcentage
    score = result.get('score', 0.0)
    formatted['score_percent'] = f"{abs(score) * 100:.1f}%"
    
    # Détermination de la couleur de la jauge
    if score > 0.5:
        formatted['gauge_color'] = 'success'
    elif score > 0:
        formatted['gauge_color'] = 'info'
    elif score < -0.5:
        formatted['gauge_color'] = 'danger'
    elif score < 0:
        formatted['gauge_color'] = 'warning'
    else:
        formatted['gauge_color'] = 'secondary'
    
    # Traduction française des sentiments
    sentiment_translations = {
        'POSITIVE': 'Positif',
        'NEGATIVE': 'Négatif',
        'NEUTRAL': 'Neutre',
        'ERROR': 'Erreur'
    }
    
    formatted['sentiment_fr'] = sentiment_translations.get(
        result.get('sentiment', 'NEUTRAL'),
        'Inconnu'
    )
    
    # Création d'un résumé texte
    if result.get('sentiment') == 'ERROR':
        formatted['summary'] = "Une erreur s'est produite lors de l'analyse."
    else:
        sentiment = formatted['sentiment_fr']
        confidence = result.get('confidence', 0.0) * 100
        formatted['summary'] = (
            f"Sentiment {sentiment.lower()} "
            f"(confiance: {confidence:.0f}%)"
        )
    
    return formatted

def validate_text(text: str, max_length: int = 1000) -> dict:
    """
    Valide le texte d'entrée
    
    Args:
        text: Texte à valider
        max_length: Longueur maximale autorisée
        
    Returns:
        Dict avec validité et message d'erreur
    """
    if not text or len(text.strip()) == 0:
        return {
            'valid': False,
            'message': 'Veuillez entrer un texte à analyser.'
        }
    
    if len(text) > max_length:
        return {
            'valid': False,
            'message': f'Le texte ne doit pas dépasser {max_length} caractères.'
        }
    
    # Vérification des caractères dangereux (simplifiée)
    dangerous_patterns = ['<script>', 'javascript:', 'onload=']
    for pattern in dangerous_patterns:
        if pattern in text.lower():
            return {
                'valid': False,
                'message': 'Le texte contient des éléments potentiellement dangereux.'
            }
    
    return {'valid': True, 'message': ''}