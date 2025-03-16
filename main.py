import logging
import time
import schedule
import pytz
from datetime import datetime
from src.news_fetcher import NewsFetcher
from src.news_processor import NewsProcessor
from src.summarizer import Summarizer
from src.delivery import DeliveryManager
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file='config/config.json'):
    """
    Load the user configuration file.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Dictionary containing user configuration
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def generate_news_summary(use_all_articles=False):
    """
    Main function to generate and deliver the news summary.
    
    Args:
        use_all_articles: Whether to use all articles or only relevant ones
    """
    logger.info("Starting news summary generation")
    
    # Initialize components
    news_fetcher = NewsFetcher()
    news_processor = NewsProcessor()
    summarizer = Summarizer()
    delivery_manager = DeliveryManager()
    
    # Fetch news articles
    logger.info("Fetching news articles")
    articles = news_fetcher.fetch_news(days=1)
    
    if not articles:
        logger.warning("No articles found")
        return
    
    # Filter and rank articles
    logger.info("Processing news articles")
    if use_all_articles:
        logger.info("Using all articles for summary generation")
        filtered_articles = news_processor.filter_articles(articles, filter_by_preferences=False)
    else:
        filtered_articles = news_processor.filter_articles(articles)
    
    ranked_articles = news_processor.rank_articles(filtered_articles)
    
    if not ranked_articles:
        logger.warning("No relevant articles found after filtering")
        return
    
    # Generate summary
    logger.info("Generating summary")
    summary = summarizer.generate_summary(ranked_articles[:20], use_all_articles=use_all_articles)  # Limit to top 20 articles
    
    # Get current date for the title
    current_date = datetime.now().strftime("%B %d, %Y")
    title = f"Stock News Summary - {current_date}"
    
    # Deliver summary
    logger.info("Delivering summary")
    success = delivery_manager.deliver_summary(summary, title)
    
    if success:
        logger.info("Summary delivered successfully")
    else:
        logger.error("Failed to deliver summary")

def schedule_daily_summary():
    """
    Schedule the daily news summary based on user configuration.
    """
    config = load_config()
    
    if not config or 'schedule' not in config:
        logger.error("Schedule configuration not found, using default (7:00 AM EST)")
        schedule_time = "07:00"
        timezone_str = "America/New_York"
    else:
        schedule_time = config['schedule'].get('time', "07:00")
        timezone_str = config['schedule'].get('timezone', "America/New_York")
    
    try:
        # Convert to the specified timezone
        timezone = pytz.timezone(timezone_str)
        logger.info(f"Scheduling daily summary at {schedule_time} {timezone_str}")
        
        # Schedule the job
        # Note: scheduled jobs will always use filtered articles by default
        schedule.every().day.at(schedule_time).do(generate_news_summary)
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"Error in scheduling: {e}")

def create_directories():
    """
    Create necessary directories if they don't exist.
    """
    directories = ['config', 'src']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def main():
    """
    Main entry point for the application.
    """
    # Create necessary directories
    create_directories()
    
    # Check if this is a one-time run or scheduled run
    import argparse
    parser = argparse.ArgumentParser(description='Stock News Summarizer')
    parser.add_argument('--now', action='store_true', help='Generate summary immediately')
    parser.add_argument('--instant', action='store_true', help='Generate summary instantly without scheduling')
    parser.add_argument('--all-articles', action='store_true', help='Generate summary from all articles, not just relevant ones')
    args = parser.parse_args()
    
    if args.now or args.instant:
        # Run immediately
        generate_news_summary(use_all_articles=args.all_articles)
        # If --instant was specified, exit after generating
        if args.instant:
            logger.info("Instant summary generation completed")
            return
    
    # If we get here, either no flags were specified or --now was used
    # In both cases, we want to schedule daily runs
    if not args.instant:
        # Schedule daily run
        schedule_daily_summary()

if __name__ == "__main__":
    main()