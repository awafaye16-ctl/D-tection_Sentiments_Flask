"""
Tests unitaires pour l'analyseur de sentiments
"""
import unittest
import sys
import os

# Ajout du répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sentiment_analyzer import SentimentAnalyzer, analyze_sentiment
from src.utils import format_sentiment_result, validate_text

class TestSentimentAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de sentiments"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Pour les tests, on utilise des valeurs factices
        self.analyzer = SentimentAnalyzer(
            api_key="test-key",
            url="https://test-api.example.com"
        )
    
    def test_empty_text(self):
        """Test avec texte vide"""
        result = self.analyzer.analyze("")
        self.assertEqual(result["sentiment"], "NEUTRAL")
        self.assertEqual(result["score"], 0.0)
        self.assertIn("Texte vide", result["label"])
    
    def test_positive_text(self):
        """Test avec texte positif (mock)"""
        # On mock la réponse API pour les tests
        class MockResponse:
            status_code = 200
            def json(self):
                return {
                    "sentiment": {
                        "document": {
                            "score": 0.85,
                            "label": "positive"
                        }
                    }
                }
        
        # Mock de requests.post
        import requests
        original_post = requests.post
        requests.post = lambda *args, **kwargs: MockResponse()
        
        try:
            result = self.analyzer.analyze("Je suis très heureux !")
            self.assertEqual(result["sentiment"], "POSITIVE")
            self.assertGreater(result["score"], 0.5)
        finally:
            requests.post = original_post
    
    def test_negative_text(self):
        """Test avec texte négatif (mock)"""
        class MockResponse:
            status_code = 200
            def json(self):
                return {
                    "sentiment": {
                        "document": {
                            "score": -0.75,
                            "label": "negative"
                        }
                    }
                }
        
        import requests
        original_post = requests.post
        requests.post = lambda *args, **kwargs: MockResponse()
        
        try:
            result = self.analyzer.analyze("Je suis très déçu.")
            self.assertEqual(result["sentiment"], "NEGATIVE")
            self.assertLess(result["score"], -0.5)
        finally:
            requests.post = original_post

class TestUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def test_format_sentiment_result(self):
        """Test du formatage des résultats"""
        result = {
            "sentiment": "POSITIVE",
            "score": 0.85,
            "label": "😊 Très positif",
            "confidence": 0.95
        }
        
        formatted = format_sentiment_result(result)
        
        self.assertEqual(formatted["sentiment_fr"], "Positif")
        self.assertEqual(formatted["css_class"], "sentiment-positive")
        self.assertEqual(formatted["score_percent"], "85.0%")
    
    def test_validate_text(self):
        """Test de validation de texte"""
        # Texte vide
        validation = validate_text("")
        self.assertFalse(validation["valid"])
        
        # Texte trop long
        long_text = "a" * 1001
        validation = validate_text(long_text, max_length=1000)
        self.assertFalse(validation["valid"])
        
        # Texte valide
        validation = validate_text("Texte normal")
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["message"], "")

class TestIntegration(unittest.TestCase):
    """Tests d'intégration"""
    
    def test_analyze_sentiment_function(self):
        """Test de la fonction de convenance"""
        # Test sans paramètres (utilise les variables d'environnement)
        result = analyze_sentiment("Test")
        # Juste vérifier que ça ne crash pas
        self.assertIn("sentiment", result)

if __name__ == "__main__":
    # Exécution des tests
    print("🧪 Exécution des tests unitaires...")
    unittest.main(verbosity=2)