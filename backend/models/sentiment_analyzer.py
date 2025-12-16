import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any
import numpy as np
from config import Config

class FinBERTSentimentAnalyzer:
    """FinBERT-based sentiment analyzer for financial/crypto news"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.FINBERT_MODEL
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_model()
    
    def _load_model(self):
        """Load FinBERT model and tokenizer"""
        try:
            print(f"Loading FinBERT model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text
        
        Returns:
            Dict with sentiment (positive/negative/neutral) and scores
        """
        try:
            inputs = self.tokenizer(text, return_tensors='pt', 
                                   truncation=True, max_length=512, 
                                   padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            scores = predictions.cpu().numpy()[0]
            
            # FinBERT labels: negative, neutral, positive
            sentiment_labels = ['negative', 'neutral', 'positive']
            sentiment_idx = np.argmax(scores)
            
            return {
                'sentiment': sentiment_labels[sentiment_idx],
                'scores': {
                    'negative': float(scores[0]),
                    'neutral': float(scores[1]),
                    'positive': float(scores[2])
                },
                'confidence': float(scores[sentiment_idx])
            }
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
                'confidence': 0.34,
                'error': str(e)
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
    
    def aggregate_sentiment(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple sentiment results into overall sentiment
        
        Returns:
            Overall sentiment score and distribution
        """
        if not sentiments:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
        
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        total = len(sentiments)
        
        # Calculate weighted sentiment score (-1 to 1)
        avg_positive = np.mean([s['scores']['positive'] for s in sentiments])
        avg_negative = np.mean([s['scores']['negative'] for s in sentiments])
        sentiment_score = avg_positive - avg_negative
        
        if sentiment_score > 0.1:
            overall = 'positive'
        elif sentiment_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': float(sentiment_score),
            'distribution': {
                'positive': positive_count / total,
                'neutral': neutral_count / total,
                'negative': negative_count / total
            },
            'counts': {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count,
                'total': total
            }
        }


class SentimentAnalysisTool:
    """MCP Tool for sentiment analysis"""
    
    def __init__(self):
        self.analyzer = None
    
    def _ensure_analyzer(self):
        """Lazy load analyzer"""
        if self.analyzer is None:
            self.analyzer = FinBERTSentimentAnalyzer()
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "analyze_sentiment",
            "description": "Analyze sentiment of cryptocurrency news using FinBERT",
            "parameters": {
                "texts": "List of news articles or texts to analyze",
                "aggregate": "Whether to return aggregated sentiment (default: True)"
            }
        }
    
    def analyze_news_sentiment(self, articles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles
        
        Args:
            articles: List of article dicts with 'title' and 'summary'
        """
        try:
            self._ensure_analyzer()
            
            # Combine title and summary for analysis
            texts = []
            for article in articles:
                title = article.get('title', '')
                summary = article.get('summary', '')
                text = f"{title}. {summary}"
                texts.append(text)
            
            # Analyze each article
            sentiments = self.analyzer.analyze_batch(texts)
            
            # Add article info to results
            for i, article in enumerate(articles):
                sentiments[i]['article'] = {
                    'title': article.get('title', ''),
                    'link': article.get('link', '')
                }
            
            # Get aggregate sentiment
            aggregate = self.analyzer.aggregate_sentiment(sentiments)
            
            return {
                "success": True,
                "individual_sentiments": sentiments,
                "aggregate_sentiment": aggregate
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        if 'articles' in params:
            return self.analyze_news_sentiment(params['articles'])
        elif 'texts' in params:
            self._ensure_analyzer()
            texts = params['texts']
            sentiments = self.analyzer.analyze_batch(texts)
            aggregate = self.analyzer.aggregate_sentiment(sentiments)
            return {
                "success": True,
                "sentiments": sentiments,
                "aggregate": aggregate
            }
        else:
            return {"success": False, "error": "No texts or articles provided"}
