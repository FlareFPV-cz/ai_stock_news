import logging
import json
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExportManager:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the ExportManager with the user configuration file.
        
        Args:
            config_file: Path to the user configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.export_dir = self._ensure_export_directory()
        
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
    
    def _ensure_export_directory(self) -> str:
        """
        Ensure that the export directory exists.
        
        Returns:
            Path to the export directory
        """
        export_dir = self.config.get('export', {}).get('directory', 'exports')
        
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
                logger.info(f"Created export directory: {export_dir}")
            except Exception as e:
                logger.error(f"Error creating export directory: {e}")
                export_dir = 'exports'  # Fallback to default
                if not os.path.exists(export_dir):
                    os.makedirs(export_dir)
                    
        return export_dir
    
    def export_to_markdown(self, summary: str, title: str, additional_data: Dict[str, Any] = None) -> str:
        """
        Export the summary to a Markdown file.
        
        Args:
            summary: The summary text
            title: The title of the summary
            additional_data: Additional data to include in the export (e.g., sentiment, stock prices)
            
        Returns:
            Path to the exported file
        """
        try:
            # Generate filename with date
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"stock_summary_{date_str}.md"
            file_path = os.path.join(self.export_dir, filename)
            
            # Create markdown content
            md_content = f"# {title}\n\n"
            
            # Add stock prices if available
            if additional_data and 'stock_prices' in additional_data and additional_data['stock_prices']:
                md_content += "## Current Stock Prices\n\n"
                md_content += "| Ticker | Price | Change | % Change |\n"
                md_content += "|--------|-------|--------|---------|\n"
                
                for ticker, data in additional_data['stock_prices'].items():
                    price = data.get('price', 'N/A')
                    change = data.get('change', 'N/A')
                    percent_change = data.get('percent_change', 'N/A')
                    
                    # Format change with color indicators (+ or -)
                    if change != 'N/A' and float(change) > 0:
                        change_str = f"+{change}"
                    else:
                        change_str = f"{change}"
                        
                    md_content += f"| {ticker} | ${price} | {change_str} | {percent_change}% |\n"
                
                md_content += "\n"
            
            # Add sentiment analysis if available
            if additional_data and 'sentiment' in additional_data and additional_data['sentiment']:
                md_content += "## Market Sentiment\n\n"
                
                for ticker, sentiment_data in additional_data['sentiment'].items():
                    positive = sentiment_data.get('positive', 0)
                    negative = sentiment_data.get('negative', 0)
                    neutral = sentiment_data.get('neutral', 0)
                    total = positive + negative + neutral
                    
                    if total > 0:
                        md_content += f"### {ticker}\n\n"
                        md_content += f"- Positive mentions: {positive}\n"
                        md_content += f"- Negative mentions: {negative}\n"
                        md_content += f"- Neutral mentions: {neutral}\n\n"
            
            # Add the main summary
            md_content += "## Summary\n\n"
            md_content += summary
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            return file_path
                
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            return ""
    
    def export_to_pdf(self, summary: str, title: str, additional_data: Dict[str, Any] = None) -> str:
        """
        Export the summary to a PDF file.
        
        Args:
            summary: The summary text
            title: The title of the summary
            additional_data: Additional data to include in the export (e.g., sentiment, stock prices)
            
        Returns:
            Path to the exported file
        """
        try:
            # First export to Markdown
            md_path = self.export_to_markdown(summary, title, additional_data)
            if not md_path:
                return ""
                
            # Generate PDF filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"stock_summary_{date_str}.pdf"
            pdf_path = os.path.join(self.export_dir, filename)
            
            try:
                # Try to import the required libraries for PDF conversion
                from weasyprint import HTML
                
                # Read the markdown content
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Convert markdown to HTML
                try:
                    import markdown
                    html_content = markdown.markdown(md_content, extensions=['tables'])
                except ImportError:
                    logger.warning("Markdown library not available, using basic HTML conversion")
                    # Basic conversion of markdown to HTML
                    html_content = f"<h1>{title}</h1>\n" + md_content.replace('\n', '<br>')
                
                # Add some basic styling
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{title}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #333366; }}
                        h2 {{ color: #333366; margin-top: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # Generate PDF
                HTML(string=styled_html).write_pdf(pdf_path)
                logger.info(f"Successfully exported to PDF: {pdf_path}")
                return pdf_path
                
            except ImportError as e:
                logger.error(f"Required libraries for PDF export not available: {e}")
                logger.info("Please install weasyprint and markdown libraries for PDF export")
                return ""
                
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            return ""