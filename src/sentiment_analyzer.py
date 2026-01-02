"""
Module d'analyse de sentiments avec Watson NLP
"""
import requests
import json
from typing import Dict, Optional

class SentimentAnalyzer:
    """Analyseur de sentiments utilisant l'API Watson NLP"""
    
    def __init__(self, api_key: str, url: str):
        """
        Initialise l'analyseur avec les credentials Watson
        
        Args:
            api_key: Clé API IBM Watson
            url: URL de l'API Watson NLP
        """
        self.api_key = api_key
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyse le sentiment d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict avec les résultats d'analyse
            
        Example:
            {
                "sentiment": "POSITIVE",
                "score": 0.85,
                "label": "😊 Très positif"
            }
        """
        if not text or len(text.strip()) == 0:
            return {
                "sentiment": "NEUTRAL",
                "score": 0.0,
                "label": "🤔 Texte vide",
                "error": "Aucun texte fourni"
            }
        
        # Préparation de la requête pour Watson NLP
        payload = {
            "text": text,
            "features": {
                "sentiment": {},
                "emotion": {
                    "targets": []
                }
            }
        }
        
        try:
            # Appel à l'API Watson
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            # Vérification de la réponse
            if response.status_code == 200:
                data = response.json()
                return self._parse_watson_response(data)
            else:
                return self._handle_api_error(response)
                
        except requests.exceptions.Timeout:
            return {
                "sentiment": "ERROR",
                "score": 0.0,
                "label": "⏰ Timeout",
                "error": "L'API Watson a mis trop de temps à répondre"
            }
        except Exception as e:
            return {
                "sentiment": "ERROR",
                "score": 0.0,
                "label": "❌ Erreur",
                "error": f"Erreur inattendue: {str(e)}"
            }
    
    def _parse_watson_response(self, data: Dict) -> Dict:
        """
        Parse la réponse de l'API Watson
        
        Args:
            data: Réponse JSON de Watson
            
        Returns:
            Résultats formatés
        """
        sentiment_data = data.get('sentiment', {})
        document_sentiment = sentiment_data.get('document', {})
        
        # Récupération du score et du label
        score = document_sentiment.get('score', 0.0)
        sentiment_label = document_sentiment.get('label', 'neutral').upper()
        
        # Mapping des sentiments vers des labels lisibles
        sentiment_map = {
            'POSITIVE': self._get_positive_label(score),
            'NEGATIVE': self._get_negative_label(score),
            'NEUTRAL': '😐 Neutre'
        }
        
        label = sentiment_map.get(sentiment_label, '😐 Neutre')
        
        return {
            "sentiment": sentiment_label,
            "score": round(score, 3),
            "label": label,
            "confidence": self._calculate_confidence(score),
            "raw_data": data  # Pour le débogage
        }
    
    def _get_positive_label(self, score: float) -> str:
        """Retourne un label approprié pour un sentiment positif"""
        if score > 0.75:
            return "😊 Très positif"
        elif score > 0.5:
            return "🙂 Positif"
        else:
            return "😌 Légèrement positif"
    
    def _get_negative_label(self, score: float) -> str:
        """Retourne un label approprié pour un sentiment négatif"""
        if score < -0.75:
            return "😠 Très négatif"
        elif score < -0.5:
            return "😞 Négatif"
        else:
            return "😕 Légèrement négatif"
    
    def _calculate_confidence(self, score: float) -> float:
        """Calcule le niveau de confiance basé sur le score"""
        absolute_score = abs(score)
        if absolute_score > 0.7:
            return 0.95  # Très confiant
        elif absolute_score > 0.4:
            return 0.80  # Confiant
        else:
            return 0.60  # Peu confiant
    
    def _handle_api_error(self, response) -> Dict:
        """Gère les erreurs de l'API Watson"""
        error_msg = f"Erreur API: {response.status_code}"
        try:
            error_data = response.json()
            error_msg = error_data.get('error', error_msg)
        except:
            pass
        
        return {
            "sentiment": "ERROR",
            "score": 0.0,
            "label": "❌ Erreur API",
            "error": error_msg
        }

# Fonction de convenance
def analyze_sentiment(text: str, api_key: Optional[str] = None, 
                     url: Optional[str] = None) -> Dict:
    """
    Fonction simplifiée pour analyser un texte
    
    Args:
        text: Texte à analyser
        api_key: Clé API Watson (optionnel, utilise les variables d'environnement)
        url: URL de l'API (optionnel)
        
    Returns:
        Résultats de l'analyse
    """
    import os
    
    # Utilise les variables d'environnement si non fournies
    if not api_key:
        api_key = os.getenv('WATSON_API_KEY', 'demo-key')
    if not url:
        url = os.getenv('WATSON_URL', 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com')
    
    analyzer = SentimentAnalyzer(api_key, url)
    return analyzer.analyze(text)