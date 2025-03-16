import json
import logging
from typing import Dict, List, Any, Optional
import groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the Summarizer with the user configuration file.
        
        Args:
            config_file: Path to the user configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.client = self._initialize_ai_client()
        
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
    
    def _initialize_ai_client(self) -> Optional[groq.Client]:
        """
        Initialize the AI client based on the configuration.
        
        Returns:
            AI client instance or None if initialization fails
        """
        if not self.config or 'ai' not in self.config:
            logger.error("AI configuration not found")
            return None
        
        ai_config = self.config['ai']
        
        if ai_config['provider'] != 'groq':
            logger.error(f"Unsupported AI provider: {ai_config['provider']}")
            return None
        
        try:
            return groq.Client(api_key=ai_config['api_key'])
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            return None
    
    def generate_summary(self, articles: List[Dict[str, Any]], use_all_articles: bool = False) -> str:
        """
        Generate a summary of the news articles using AI.
        
        Args:
            articles: List of news articles
            use_all_articles: Whether to use all articles without focusing on specific tickers/keywords
            
        Returns:
            Summary text
        """
        if not self.client:
            logger.error("AI client not initialized")
            return "Error: AI summarization service not available."
        
        if not articles:
            return "No relevant news articles found for your preferences."
        
        # Prepare the prompt for the AI
        prompt = self._prepare_prompt(articles, use_all_articles)
        
        try:
            # Use Groq's LLM API to generate the summary
            model = self.config['ai'].get('model', 'llama3-8b-8192')  # Get model from config or use default
            logger.info(f"AI client model {model} loaded")
            # Get max_tokens from config or use default value
            max_tokens = self.config['ai'].get('max_tokens', 8192)
            logger.info(f"Using max_tokens: {max_tokens}")
            
            response = self.client.chat.completions.create(
                model=model,  # Using model specified in config
                messages=[
                    {"role": "system", "content": "You are a financial news analyst assistant that provides concise, informative summaries of financial news. Focus on key information relevant to investors and market trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error: Unable to generate summary at this time."
    
    def _prepare_prompt(self, articles: List[Dict[str, Any]], use_all_articles: bool = False) -> str:
        """
        Prepare the prompt for the AI based on the articles.
        
        Args:
            articles: List of news articles
            use_all_articles: Whether to use all articles without focusing on specific tickers/keywords
            
        Returns:
            Formatted prompt string
        """
        # Extract user preferences for context
        tickers = self.config.get('tickers', [])
        keywords = self.config.get('keywords', [])
        
        # Format articles for the prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i}:\n"
            articles_text += f"Title: {article.get('title', 'No title')}\n"
            articles_text += f"Source: {article.get('source', 'Unknown')}\n"
            articles_text += f"Date: {article.get('published', 'Unknown date')}\n"
            articles_text += f"Summary: {article.get('summary', 'No summary available')}\n"
            articles_text += f"URL: {article.get('link', 'No URL')}\n\n"
        
        # Construct the prompt - exclude tickers and keywords if use_all_articles is True
        if use_all_articles:
            prompt = f"""Please provide a concise summary of the following financial news articles.

Here are the articles to summarize:

{articles_text}

Please create a well-structured summary that:
1. Identifies key market trends and insights
2. Organizes information by topic or relevance
3. Is concise and easy to read (around {self.config['ai'].get('summary_length', '300-1000')} words)
4. Includes a brief market outlook based on the news"""
        else:
            prompt = f"""Please provide a concise summary of the following financial news articles.

Focus on these stocks/tickers of interest: {', '.join(tickers)}
And these keywords/topics: {', '.join(keywords)}

Here are the articles to summarize:

{articles_text}

Please create a well-structured summary that:
1. Highlights the most important news for the specified tickers
2. Identifies key market trends and insights
3. Organizes information by topic or relevance
4. Is concise and easy to read (around {self.config['ai'].get('summary_length', '300-1000')} words)
5. Includes a brief market outlook based on the news"""
        
        return prompt