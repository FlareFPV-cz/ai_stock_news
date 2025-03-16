import logging
from typing import Dict, List, Any, Optional
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsProcessor:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the NewsProcessor with the user configuration file.
        
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
            import json
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def filter_articles(self, articles: List[Dict[str, Any]], filter_by_preferences: bool = True) -> List[Dict[str, Any]]:
        """
        Filter articles based on user preferences (tickers and keywords).
        
        Args:
            articles: List of news articles
            filter_by_preferences: Whether to filter articles by user preferences (tickers and keywords)
            
        Returns:
            Filtered list of news articles
        """
        if not articles:
            return []
        
        # If filter_by_preferences is False, return all articles without filtering
        if not filter_by_preferences:
            logger.info("Bypassing filtering, returning all articles")
            return articles
        
        # Get user preferences
        tickers = self.config.get('tickers', [])
        keywords = self.config.get('keywords', [])
        
        # If no filtering criteria, return all articles
        if not tickers and not keywords:
            logger.info("No filtering criteria specified, returning all articles")
            return articles
            
        # If we have no articles to filter, return empty list
        if not articles:
            logger.info("No articles to filter")
            return []
        
        filtered_articles = []
        
        # Compile regex patterns for tickers and keywords
        ticker_patterns = [re.compile(r'\b' + re.escape(ticker) + r'\b', re.IGNORECASE) for ticker in tickers]
        # Use more flexible matching for keywords (don't require word boundaries)
        keyword_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]
        
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = f"{title} {summary}"
            
            # Check if article contains any ticker
            ticker_match = any(pattern.search(content) for pattern in ticker_patterns) if ticker_patterns else False
            
            # Check if article contains any keyword
            keyword_match = any(pattern.search(content) for pattern in keyword_patterns) if keyword_patterns else False
            
            # If article matches any ticker OR keyword, include it
            if ticker_match or keyword_match or (not tickers and not keywords):
                filtered_articles.append(article)
        
        logger.info(f"Filtered {len(articles)} articles down to {len(filtered_articles)} relevant articles")
        return filtered_articles
    
    def rank_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank articles based on relevance to user preferences.
        
        Args:
            articles: List of news articles
            
        Returns:
            Ranked list of news articles
        """
        if not articles:
            return []
        
        # Get user preferences
        tickers = self.config.get('tickers', [])
        keywords = self.config.get('keywords', [])
        
        # If no ranking criteria, return articles as is
        if not tickers and not keywords:
            return articles
        
        # Compile regex patterns for tickers and keywords
        ticker_patterns = [re.compile(r'\b' + re.escape(ticker) + r'\b', re.IGNORECASE) for ticker in tickers]
        # Use more flexible matching for keywords (don't require word boundaries)
        keyword_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]
        
        # Calculate relevance score for each article
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = f"{title} {summary}"
            
            # Count ticker matches
            ticker_count = sum(len(pattern.findall(content)) for pattern in ticker_patterns) if ticker_patterns else 0
            
            # Count keyword matches
            keyword_count = sum(len(pattern.findall(content)) for pattern in keyword_patterns) if keyword_patterns else 0
            
            # Calculate relevance score (title matches count more)
            title_ticker_count = sum(len(pattern.findall(title)) for pattern in ticker_patterns) if ticker_patterns else 0
            title_keyword_count = sum(len(pattern.findall(title)) for pattern in keyword_patterns) if keyword_patterns else 0
            
            # Final score calculation (title matches have 2x weight)
            relevance_score = ticker_count + keyword_count + (title_ticker_count + title_keyword_count) * 2
            
            # Add score to article
            article['relevance_score'] = relevance_score
        
        # Sort articles by relevance score (highest first)
        ranked_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return ranked_articles