# Stock News Summarizer

A Python application that delivers a daily morning summary of stock-related news based on user-defined preferences. The application fetches news from various financial sources, filters them according to your interests, generates concise AI-powered summaries, and delivers them through your preferred notification channels.

## Features

- **News Aggregation**: Collects financial news from CNBC, WSJ, Bloomberg, Reuters, MarketWatch and other sources via RSS feeds
- **Customization**: Filter news based on preferred sources, stocks/tickers, and keywords
- **AI Summarization**: Uses Groq API to generate concise, easy-to-read summaries
- **Multiple Delivery Methods**: Send summaries via ntfy push notifications, email, or messaging platforms (Telegram/Discord)
- **Smart Filtering**: Ranks articles by relevance to your interests
- **Scheduled Delivery**: Automatically delivers summaries at your preferred time each day

## Optional Features

- Sentiment analysis on stock-related articles
- Stock price movements alongside news
- PDF/Markdown summary option

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
4. Run the application: `python main.py`

## Configuration

Edit the `config/config.json` file to customize your news preferences and delivery options.

```json
{
  "news_sources": ["CNBC", "WSJ", "Bloomberg", "Reuters", "MarketWatch"],
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "keywords": ["interest rates", "tech earnings", "market analysis"],
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
