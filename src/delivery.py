import json
import logging
import time
from typing import Dict, Any, Optional
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeliveryManager:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the DeliveryManager with the user configuration file.
        
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
    
    def deliver_summary(self, summary: str, title: str = "Stock News Summary") -> bool:
        """
        Deliver the summary using all enabled delivery methods.
        
        Args:
            summary: The summary text to deliver
            title: The title of the summary
            
        Returns:
            True if at least one delivery method succeeded, False otherwise
        """
        if not self.config or 'delivery' not in self.config:
            logger.error("Delivery configuration not found")
            return False
        
        delivery_config = self.config['delivery']
        success = False
        
        # Try each enabled delivery method
        if delivery_config.get('ntfy', {}).get('enabled', False):
            if self._deliver_via_ntfy(summary, title):
                success = True
        
        if delivery_config.get('email', {}).get('enabled', False):
            if self._deliver_via_email(summary, title):
                success = True
        
        if delivery_config.get('telegram', {}).get('enabled', False):
            if self._deliver_via_telegram(summary, title):
                success = True
        
        if delivery_config.get('discord', {}).get('enabled', False):
            if self._deliver_via_discord(summary, title):
                success = True
        
        return success
    
    def _deliver_via_ntfy(self, summary: str, title: str) -> bool:
        """
        Deliver the summary via ntfy push notification.
        
        Args:
            summary: The summary text to deliver
            title: The title of the summary
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            ntfy_config = self.config['delivery']['ntfy']
            topic = ntfy_config.get('topic')
            
            if not topic:
                logger.error("ntfy topic not configured")
                return False
            
            # Send notification to ntfy.sh
            response = requests.post(
                f"https://ntfy.sh/{topic}",
                data=summary,
                headers={
                    "Title": title,
                    "Priority": "default",
                    "Tags": "chart_with_upwards_trend"
                }
            )
            
            if response.status_code == 200:
                logger.info("Successfully delivered summary via ntfy")
                return True
            else:
                logger.error(f"Failed to deliver via ntfy: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error delivering via ntfy: {e}")
            return False
    
    def _deliver_via_email(self, summary: str, title: str) -> bool:
        """
        Deliver the summary via email.
        
        Args:
            summary: The summary text to deliver
            title: The title of the summary
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            email_config = self.config['delivery']['email']
            recipient = email_config.get('address')
            
            if not recipient:
                logger.error("Email address not configured")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['Subject'] = title
            msg['From'] = email_config.get('sender_email')  # Use the configured sender email
            msg['To'] = recipient
            
            # Add summary as HTML content
            html_content = f"""<html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #333366; }}
                    .footer {{ font-size: 12px; color: #999; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{title}</h1>
                    {summary.replace('\n', '<br>')}
                    <div class="footer">
                        <p>This summary was generated automatically by Stock News Summarizer.</p>
                    </div>
                </div>
            </body>
            </html>"""
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Get email configuration
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            sender_email = email_config.get('sender_email', recipient)  # Default to recipient if not specified
            password = email_config.get('password')
            
            if not password:
                logger.error("Email password not configured in config.json")
                return False
                
            # Send the email with improved error handling and logging
            max_retries = 2
            retry_count = 0
            timeout = 300  # More reasonable timeout value
            
            while retry_count <= max_retries:
                try:
                    logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port} (Attempt {retry_count + 1}/{max_retries + 1})")
                    
                    # Try to use SSL first if port is 465, otherwise use standard SMTP with STARTTLS
                    if smtp_port == 465:
                        logger.info("Using SMTP_SSL connection")
                        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                            server.set_debuglevel(2)
                            
                            logger.info("Identifying ourselves to the server (EHLO)")
                            server.ehlo()
                            
                            logger.info(f"Attempting to log in as {sender_email}")
                            server.login(sender_email, password)
                            
                            logger.info("Sending email message")
                            server.send_message(msg)
                            
                            logger.info(f"Successfully sent email to {recipient}")
                            return True
                    else:
                        logger.info("Using standard SMTP connection with STARTTLS")
                        with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
                            server.set_debuglevel(1)
                            
                            logger.info("Identifying ourselves to the server (EHLO)")
                            server.ehlo()
                            
                            logger.info("Starting TLS encryption")
                            server.starttls()
                            
                            logger.info("Re-identifying ourselves over TLS (EHLO)")
                            server.ehlo()
                            
                            logger.info(f"Attempting to log in as {sender_email}")
                            server.login(sender_email, password)
                            
                            logger.info("Sending email message")
                            server.send_message(msg)
                            
                            logger.info(f"Successfully sent email to {recipient}")
                            return True
                            
                except smtplib.SMTPAuthenticationError:
                    logger.error("Failed to authenticate with email server. If using Gmail, you need to use an App Password instead of your regular password.")
                    # No retry for authentication errors
                    return False
                    
                except smtplib.SMTPSenderRefused:
                    logger.error(f"Email server rejected sender address: {sender_email}. Verify the address is correct.")
                    return False
                    
                except smtplib.SMTPRecipientsRefused:
                    logger.error(f"Email server rejected recipient address: {recipient}. Verify the address is correct.")
                    return False
                    
                except smtplib.SMTPDataError as e:
                    logger.error(f"SMTP data error: {e}. The server rejected the message data.")
                    return False
                    
                except (TimeoutError, smtplib.SMTPServerDisconnected, ConnectionRefusedError) as e:
                    if retry_count < max_retries:
                        wait_time = (retry_count + 1) * 3  # Progressive backoff: 3s, 6s
                        logger.warning(f"Connection issue: {str(e)}. Retrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
                        time.sleep(wait_time)
                        retry_count += 1
                    else:
                        if isinstance(e, TimeoutError):
                            logger.error("Connection timed out after multiple attempts. Check your network connection and firewall settings.")
                        elif isinstance(e, ConnectionRefusedError):
                            logger.error("Connection refused after multiple attempts. Verify SMTP server address and port are correct.")
                        else:
                            logger.error(f"Server disconnected: {e}. Verify your SMTP settings and try again.")
                        return False
                        
                except smtplib.SMTPException as smtp_error:
                    logger.error(f"SMTP error occurred: {smtp_error}")
                    return False
                    
                except Exception as e:
                    logger.error(f"Unexpected error during email delivery: {e}")
                    return False
            
            return True
                
        except Exception as e:
            logger.error(f"Error delivering via email: {e}")
            return False
    
    def _deliver_via_telegram(self, summary: str, title: str) -> bool:
        """
        Deliver the summary via Telegram bot.
        
        Args:
            summary: The summary text to deliver
            title: The title of the summary
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            telegram_config = self.config['delivery']['telegram']
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                logger.error("Telegram bot_token or chat_id not configured")
                return False
            
            # Format message for Telegram
            message = f"*{title}*\n\n{summary}"
            
            # Send message via Telegram Bot API
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                logger.info("Successfully delivered summary via Telegram")
                return True
            else:
                logger.error(f"Failed to deliver via Telegram: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error delivering via Telegram: {e}")
            return False
    
    def _deliver_via_discord(self, summary: str, title: str) -> bool:
        """
        Deliver the summary via Discord webhook.
        
        Args:
            summary: The summary text to deliver
            title: The title of the summary
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            discord_config = self.config['delivery']['discord']
            webhook_url = discord_config.get('webhook_url')
            
            if not webhook_url:
                logger.error("Discord webhook_url not configured")
                return False
            
            # Discord has a 2000 character limit for messages
            # First message includes the title
            first_message = f"**{title}**\n\n"
            max_content_length = 2000 - len(first_message)
            
            if len(summary) <= max_content_length:
                # Summary fits in a single message
                response = requests.post(
                    webhook_url,
                    json={
                        "content": first_message + summary
                    }
                )
                
                if response.status_code != 204:
                    logger.error(f"Failed to deliver via Discord: {response.status_code} {response.text}")
                    return False
            else:
                # Need to split the summary into multiple messages
                # Send the first message with the title
                first_part = summary[:max_content_length]
                response = requests.post(
                    webhook_url,
                    json={
                        "content": first_message + first_part
                    }
                )
                
                if response.status_code != 204:
                    logger.error(f"Failed to deliver first part via Discord: {response.status_code} {response.text}")
                    return False
                
                # Send remaining parts in chunks of 2000 characters
                remaining = summary[max_content_length:]
                chunk_size = 1950  # Slightly less than 2000 to be safe
                
                for i in range(0, len(remaining), chunk_size):
                    chunk = remaining[i:i+chunk_size]
                    response = requests.post(
                        webhook_url,
                        json={
                            "content": chunk
                        }
                    )
                    
                    if response.status_code != 204:
                        logger.error(f"Failed to deliver part {i//chunk_size + 2} via Discord: {response.status_code} {response.text}")
                        return False
                    
                    # Add a small delay between messages to avoid rate limiting
                    time.sleep(0.5)
            
            logger.info("Successfully delivered summary via Discord")
            return True
                
        except Exception as e:
            logger.error(f"Error delivering via Discord: {e}")
            return False