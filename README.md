# Stock News Summarizer

A Python application that delivers a daily morning summary of stock-related news based on user-defined preferences. The application fetches news from various financial sources, filters them according to your interests, generates concise AI-powered summaries, and delivers them through your preferred notification channels.

## Features

- **News Aggregation**: Collects financial news from CNBC, WSJ, Bloomberg, Reuters, MarketWatch and other sources via RSS feeds
- **Customization**: Filter news based on preferred sources, stocks/tickers, and keywords
- **AI Summarization**: Uses Groq API to generate concise, easy-to-read summaries
- **Multiple Delivery Methods**: Send summaries via ntfy push notifications, email, or messaging platforms (Telegram/Discord/Teams)
- **Smart Filtering**: Ranks articles by relevance to your interests
- **Scheduled Delivery**: Automatically delivers summaries at your preferred time each day
- **Sentiment Analysis**: Analyzes sentiment of stock-related articles
- **Stock Price Movements**: Includes current stock prices alongside news
- **Export Options**: Export summaries to Markdown or PDF formats

## Project Structure

```

├── config/
│   ├── config.json         # User configuration file
│   └── sources.json        # News sources configuration
├── src/
│   ├── news_fetcher.py     # Module for fetching news from various sources
│   ├── news_processor.py   # Module for filtering and processing news
│   ├── summarizer.py       # Module for AI-based summarization
│   ├── delivery.py         # Module for delivering summaries
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup and Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your preferences in `config/config.json`
4. Run the application: `python main.py` or `python main.py --instant` or `python main.py --instant --all-articles --export markdown`

#### Sample console log
```python
$ python main.py --instant --export markdown --all-articles
2025-03-16 11:15:37,798 - __main__ - INFO - Starting news summary generation
2025-03-16 11:15:38,796 - __main__ - INFO - Fetching news articles
2025-03-16 11:15:38,803 - src.news_fetcher - INFO - Fetching news from CNBC
2025-03-16 11:15:41,405 - src.news_fetcher - INFO - Fetching news from Wall Street Journal
2025-03-16 11:15:42,879 - src.news_fetcher - INFO - Fetching news from Bloomberg
2025-03-16 11:15:46,402 - src.news_fetcher - INFO - Fetched 26 articles from 3 sources
2025-03-16 11:15:46,403 - __main__ - INFO - Processing news articles
2025-03-16 11:15:46,403 - __main__ - INFO - Using all articles for summary generation
2025-03-16 11:15:46,403 - src.news_processor - INFO - Bypassing filtering, returning all articles
2025-03-16 11:15:46,403 - __main__ - INFO - Analyzing sentiment of articles
2025-03-16 11:15:46,403 - __main__ - INFO - Fetching current stock prices
2025-03-16 11:15:53,013 - __main__ - INFO - Generating summary
2025-03-16 11:15:53,013 - src.summarizer - INFO - AI client model qwen-qwq-32b loaded
2025-03-16 11:15:53,013 - src.summarizer - INFO - Using max_tokens: 8192
2025-03-16 11:16:02,895 - httpx - INFO - HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2025-03-16 11:16:02,905 - __main__ - INFO - Exported summary to Markdown: exports\stock_summary_2025-03-16.md
2025-03-16 11:16:02,905 - __main__ - INFO - Delivering summary
2025-03-16 11:16:09,200 - src.delivery - INFO - Successfully delivered summary via Discord
2025-03-16 11:16:09,202 - __main__ - INFO - Summary delivered successfully
2025-03-16 11:16:09,202 - __main__ - INFO - Instant summary generation completed
```

## Configuration

Edit the `config/config.json` file to customize your news preferences and delivery options.

```json
{
  "news_sources": ["CNBC", "WSJ", "Bloomberg", "Reuters", "MarketWatch"],
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "keywords": ["interest rates", "tech earnings", "market analysis"],
  "stock_prices": {
    "provider": "alphavantage",
    "api_key": ""
  },
  "sentiment": {
    "use_ai": true
  },
  "export": {
    "directory": "exports"
  },
  "delivery": {
    "ntfy": {
      "enabled": true,
      "topic": "your-ntfy-topic"
    },
    "email": {
      "enabled": false,
      "address": "your-email@example.com",
      "sender_email": "your-sender-email@example.com",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "password": "your-app-password"
    },
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "discord": {
      "enabled": false,
      "webhook_url": ""
    }
  },
  "ai": {
    "provider": "groq",
    "api_key": "YOUR_GROQ_API_KEY",
    "model": "llama3-8b-8192",
    "summary_length": "300-1000",
    "max_tokens": 8192
  },
  "schedule": {
    "time": "07:00",
    "timezone": "America/New_York"
  }
}
```

## Delivery Methods
### ntfy Push Notifications
For instant notifications on your devices, enable the ntfy delivery method and specify your topic. Install the ntfy app on your devices and subscribe to your topic to receive notifications.

### Email
To receive summaries via email:

- Set enabled to true
- Provide your email address in address
- Configure SMTP settings for your email provider
- For Gmail, use an App Password instead of your regular password
### Telegram
To receive summaries via Telegram:

- Create a Telegram bot using BotFather and get the bot token
- Find your chat ID
- Configure both in the settings
### Discord
To receive summaries in a Discord channel:

- Create a webhook in your Discord server
- Add the webhook URL to the configuration
### Microsoft Teams
To receive summaries in a Microsoft Teams channel:

- Create an incoming webhook in your Teams channel
  - In Teams, go to the channel where you want to add the webhook
  - Click the "..." menu next to the channel name
  - Select "Connectors"
  - Find "Incoming Webhook" and click "Configure"
  - Name your webhook and upload an icon if desired
  - Click "Create" and copy the webhook URL
- Add the webhook URL to the configuration
- Set enabled to true in the teams section
## News Sources
The application comes pre-configured with RSS feeds from major financial news sources:

- CNBC (Finance, Investing, Markets)
- Wall Street Journal (Markets, Business)
- Bloomberg (Markets, Technology, Wealth)
- Reuters (Business & Finance, Markets)
- MarketWatch (Top Stories, Market Pulse)
You can customize the sources in config/sources.json .

## Advanced Usage
### Filtering Articles
The application filters articles based on your specified tickers and keywords. Articles that mention your tickers or keywords will be included in the summary.

### Article Ranking
Articles are ranked by relevance to your interests, with higher priority given to articles that mention your tickers or keywords in the title.

### AI Summarization
The application uses Groq's AI models to generate concise summaries. You can configure:
- The AI model to use
- Maximum token length
- Desired summary length
## Requirements
- Python 3.7+
- Internet connection
- Groq API key for AI summarization
