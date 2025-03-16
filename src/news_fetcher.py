import json
import logging
import feedparser
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, sources_file: str = 'config/sources.json', config_file: str = 'config/config.json'):
        """
        Initialize the NewsFetcher with the sources and user configuration files.
        
        Args:
            sources_file: Path to the sources configuration file
            config_file: Path to the user configuration file
        """
        self.sources_file = sources_file
        self.config_file = config_file
        self.sources = self._load_sources()
        self.config = self._load_config()
        
    def _load_sources(self) -> Dict[str, Any]:
        """
        Load news sources from the sources configuration file.
        
        Returns:
            Dictionary containing news sources configuration
        """
        try:
            with open(self.sources_file, 'r') as f:
                return json.load(f).get('sources', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading sources: {e}")
            return {}
    
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
    
    def fetch_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch news from all configured sources based on user preferences.
        
        Args:
            days: Number of days to look back for news
            
        Returns:
            List of news articles
        """
        if not self.sources or not self.config:
            logger.error("Sources or configuration not loaded properly")
            return []
        
        # Get user-preferred sources
        preferred_sources = self.config.get('news_sources', [])
        if not preferred_sources:
            logger.warning("No news sources specified in configuration")
            return []
        
        # Calculate the cutoff date for news articles
        # Ensure cutoff_date is timezone-naive for consistent comparison
        cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days)
        
        all_articles = []
        
        # Fetch news from each preferred source
        for source_id in preferred_sources:
            if source_id not in self.sources:
                logger.warning(f"Source {source_id} not found in sources configuration")
                continue
            
            source = self.sources[source_id]
            logger.info(f"Fetching news from {source['name']}")
            
            for feed_info in source.get('rss_feeds', []):
                try:
                    # Parse the RSS feed
                    feed = feedparser.parse(feed_info['url'])
                    
                    # Add a small delay to avoid overwhelming the servers
                    time.sleep(0.5)
                    
                    # Process each entry in the feed
                    for entry in feed.entries:
                        # Parse the publication date
                        published = self._parse_date(entry.get('published', ''))
                        
                        # Skip articles older than the cutoff date
                        if published and published < cutoff_date:
                            continue
                        
                        # Create article object
                        article = {
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', entry.get('description', 'No summary available')),
                            'published': entry.get('published', 'Unknown date'),
                            'published_parsed': published,
                            'source': source['name'],
                            'source_id': source_id,
                            'category': feed_info.get('category', 'General')
                        }
                        
                        all_articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error fetching feed {feed_info['url']}: {e}")
        
        # Sort articles by publication date (newest first)
        all_articles.sort(key=lambda x: x.get('published_parsed', datetime.min), reverse=True)
        
        logger.info(f"Fetched {len(all_articles)} articles from {len(preferred_sources)} sources")
        return all_articles
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: Date string from RSS feed
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        try:
            # Try to parse using feedparser's time tuple
            time_tuple = feedparser._parse_date(date_str)
            if time_tuple:
                # Create a timezone-naive datetime object
                return datetime(*time_tuple[:6]).replace(tzinfo=None)
        except Exception:
            pass
        
        # Try common date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
            '%a, %d %b %Y %H:%M:%S %Z',  # RFC 822 with timezone name
            '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601
            '%Y-%m-%dT%H:%M:%SZ',        # ISO 8601 UTC
            '%Y-%m-%d %H:%M:%S',         # Simple format
            '%a %b %d %H:%M:%S %Y',      # Another common format
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Ensure timezone-naive datetime for consistent comparison
                return dt.replace(tzinfo=None) if dt.tzinfo else dt
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None