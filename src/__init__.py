"""
Package sentiment_analysis - Analyse de sentiments avec Watson AI
"""

from .sentiment_analyzer import SentimentAnalyzer, analyze_sentiment
from .utils import format_sentiment_result, validate_text

__version__ = "1.0.0"
__author__ = "IBM Skills Network"
__description__ = "Package d'analyse de sentiments utilisant Watson AI"

__all__ = [
    'SentimentAnalyzer',
    'analyze_sentiment', 
    'format_sentiment_result',
    'validate_text'
]

print(f"✅ Package sentiment_analysis v{__version__} chargé avec succès!")