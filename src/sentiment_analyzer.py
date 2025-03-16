import logging
import json
from typing import Dict, List, Any, Optional
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the SentimentAnalyzer with the user configuration file.
        
        Args:
            config_file: Path to the user configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load user configuration from the configuration file.
        
        Returns:
            Dictionary containing user configuration
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def analyze_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sentiment for each article and aggregate by ticker.
        
        Args:
            articles: List of news articles
            
        Returns:
            Dictionary with sentiment analysis results by ticker
        """
        if not articles:
            return {}
        
        # Get user-defined tickers
        tickers = self.config.get('tickers', [])
        if not tickers:
            logger.warning("No tickers specified in configuration for sentiment analysis")
            return {}
        
        # Initialize sentiment results for each ticker
        sentiment_results = {ticker: {'positive': 0, 'negative': 0, 'neutral': 0, 'articles': []} for ticker in tickers}
        
        # Compile regex patterns for tickers
        ticker_patterns = {ticker: re.compile(r'\b' + re.escape(ticker) + r'\b', re.IGNORECASE) for ticker in tickers}
        
        # Process each article
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = f"{title} {summary}"
            
            # Determine which tickers are mentioned in the article
            mentioned_tickers = [ticker for ticker, pattern in ticker_patterns.items() if pattern.search(content)]
            
            if not mentioned_tickers:
                continue
                
            # Analyze sentiment for this article
            article_sentiment = self._analyze_article_sentiment(content)
            
            # Update sentiment counts for each mentioned ticker
            for ticker in mentioned_tickers:
                sentiment_results[ticker][article_sentiment] += 1
                sentiment_results[ticker]['articles'].append({
                    'title': title,
                    'sentiment': article_sentiment,
                    'source': article.get('source', 'Unknown'),
                    'link': article.get('link', '')
                })
        
        return sentiment_results
    
    def _analyze_article_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of an article text.
        
        Args:
            text: The article text to analyze
            
        Returns:
            Sentiment classification ('positive', 'negative', or 'neutral')
        """
        # Check if we should use the AI model for sentiment analysis
        if self.config.get('sentiment', {}).get('use_ai', False):
            return self._analyze_sentiment_with_ai(text)
        
        # Simple rule-based sentiment analysis as fallback
        positive_words = ['up', 'rise', 'gain', 'growth', 'profit', 'positive', 'bullish', 'outperform', 
                         'beat', 'exceed', 'strong', 'success', 'opportunity', 'improve', 'advantage']
        
        negative_words = ['down', 'fall', 'drop', 'decline', 'loss', 'negative', 'bearish', 'underperform',
                         'miss', 'weak', 'fail', 'risk', 'concern', 'problem', 'challenge']
        
        # Count occurrences of positive and negative words
        positive_count = sum(1 for word in positive_words if re.search(r'\b' + re.escape(word) + r'\b', text.lower()))
        negative_count = sum(1 for word in negative_words if re.search(r'\b' + re.escape(word) + r'\b', text.lower()))
        
        # Determine sentiment based on counts
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_sentiment_with_ai(self, text: str) -> str:
        """
        Analyze sentiment using the configured AI model.
        
        Args:
            text: The text to analyze
            
        Returns:
            Sentiment classification ('positive', 'negative', or 'neutral')
        """
        try:
            # Use the same AI client as the summarizer
            import groq
            
            ai_config = self.config.get('ai', {})
            client = groq.Client(api_key=ai_config.get('api_key', ''))
            model = ai_config.get('model', 'llama3-8b-8192')
            
            # Create a prompt for sentiment analysis
            prompt = f"""Analyze the sentiment of the following financial news text regarding stock market or company performance. 
            Classify it as 'positive', 'negative', or 'neutral'.
            
            Text: {text}
            
            Sentiment:"""
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analyzer that classifies text as positive, negative, or neutral."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            # Extract the sentiment from the response
            content = response.choices[0].message.content.lower()
            
            if 'positive' in content:
                return 'positive'
            elif 'negative' in content:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment with AI: {e}")
            # Fall back to rule-based analysis
            return self._analyze_article_sentiment(text)