import os
import zipfile
import asyncio
import logging
import requests
from urllib.parse import urlparse, urljoin
from pathlib import Path
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
DOWNLOAD_FOLDER = 'site_download'
ZIP_FILE_NAME = 'site_download.zip'
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB limit
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file limit

class WebsiteDownloader:
    def __init__(self):
        self.downloaded_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def AHMD_is_valid_url(self, url, base_domain):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            if not parsed.netloc:
                return False
                
            # Allow same domain and subdomains
            if parsed.netloc == base_parsed.netloc or parsed.netloc.endswith('.' + base_parsed.netloc):
                return True
                
            return False
        except:
            return False
    
    def hmd_download_file(self, url, folder_path):
        """Download a single file"""
        try:
            response = self.session.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Get filename from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = 'index.html'
                
            # Create directory structure
            path_parts = parsed.path.split('/')[:-1]
            if path_parts:
                dir_path = os.path.join(folder_path, *path_parts)
                os.makedirs(dir_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, parsed.path.lstrip('/'))
            if not file_path:
                file_path = os.path.join(folder_path, 'index.html')
                
            # Ensure we have a file extension
            if not os.path.splitext(file_path)[1]:
                file_path += '.html'
            
            # Download file with size limit
            file_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_size += len(chunk)
                        if file_size > MAX_FILE_SIZE:
                            logger.warning(f"File too large: {url}")
                            return None
                        f.write(chunk)
            
            return file_path
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    def Ahmad_extract_links(self, html_content, base_url):
        """Extract all links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        # Extract all possible resource links
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'source']):
            url = None
            if tag.name == 'a' and tag.get('href'):
                url = urljoin(base_url, tag['href'])
            elif tag.name == 'link' and tag.get('href'):
                url = urljoin(base_url, tag['href'])
            elif tag.name == 'script' and tag.get('src'):
                url = urljoin(base_url, tag['src'])
            elif tag.name in ['img', 'source'] and tag.get('src'):
                url = urljoin(base_url, tag['src'])
            elif tag.name == 'img' and tag.get('srcset'):
                # Handle srcset attribute
                srcset = tag['srcset'].split(',')
                for src in srcset:
                    url_part = src.strip().split(' ')[0]
                    url = urljoin(base_url, url_part)
                    if url:
                        links.add(url)
                continue
            
            if url and url not in self.downloaded_urls:
                links.add(url)
        
        return links
    
    def hmoudi_download_website(self, url, folder_path, max_pages=20):
        """Download a website recursively"""
        os.makedirs(folder_path, exist_ok=True)
        base_domain = urlparse(url).netloc
        queue = [url]
        downloaded_pages = 0
        total_size = 0
        
        while queue and downloaded_pages < max_pages and total_size < MAX_DOWNLOAD_SIZE:
            current_url = queue.pop(0)
            
            if current_url in self.downloaded_urls:
                continue
                
            self.downloaded_urls.add(current_url)
            
            try:
                # Check if this is an HTML page or a resource file
                parsed = urlparse(current_url)
                if any(parsed.path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg']):
                    # Download resource file
                    file_path = self.hmd_download_file(current_url, folder_path)
                    if file_path:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        logger.info(f"Downloaded resource: {current_url} ({file_size} bytes)")
                else:
                    # Download HTML page and extract links
                    response = self.session.get(current_url, timeout=10)
                    response.raise_for_status()
                    
                    # Save HTML file
                    file_path = self.hmd_download_file(current_url, folder_path)
                    if file_path:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        downloaded_pages += 1
                        logger.info(f"Downloaded page {downloaded_pages}: {current_url} ({file_size} bytes)")
                    
                    # Extract links from HTML
                    if response.headers.get('content-type', '').startswith('text/html'):
                        links = self.Ahmad_extract_links(response.content, current_url)
                        for link in links:
                            if self.AHMD_is_valid_url(link, url) and link not in self.downloaded_urls:
                                queue.append(link)
            
            except Exception as e:
                logger.error(f"Error processing {current_url}: {e}")
                continue
        
        return total_size

class WebsiteDownloaderBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.downloader = WebsiteDownloader()
        self.hmoudi_setup_handlers()
        self.active_downloads = {}
        
    def hmoudi_setup_handlers(self):
        """Setup command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.AHMD_start))
        self.app.add_handler(CommandHandler("help", self.hmd_help))
        self.app.add_handler(CommandHandler("status", self.Ahmad_status))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.hmoudi_handle_url))
        
    async def AHMD_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        user = update.effective_user
        welcome_text = (
            f"Hello {user.first_name}! 👋\n\n"
            "I'm a website downloader bot. Send me a URL and I'll download the website "
            "and send it back to you as a ZIP file.\n\n"
            "Available commands:\n"
            "/start - Show this welcome message\n"
            "/help - Display help information\n"
            "/status - Check your current download status\n\n"
            "Note: This is a basic downloader that works without wget. "
            "It may not download all resources like a full wget mirror would."
        )
        await update.message.reply_text(welcome_text)
        
    async def hmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when the command /help is issued."""
        help_text = (
            "How to use this bot:\n\n"
            "1. Simply send me a valid URL (starting with http:// or https://)\n"
            "2. I'll download the website using Python libraries\n"
            "3. Once downloaded, I'll compress it into a ZIP file\n"
            "4. I'll send the ZIP file back to you\n\n"
            "Important notes:\n"
            "- I can download up to 20 pages and 50MB total\n"
            "- Complex websites might not download completely\n"
            "- Files are automatically deleted after 3 minutes for privacy\n"
            "- Use the /status command to check your download progress\n\n"
            "Please respect website terms of service and robots.txt files."
        )
        await update.message.reply_text(help_text)
        
    async def Ahmad_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check the status of user's download"""
        user_id = update.effective_user.id
        if user_id in self.active_downloads:
            status = self.active_downloads[user_id]
            await update.message.reply_text(f"Your download status: {status}")
        else:
            await update.message.reply_text("You don't have any active downloads.")
    
    def hmd_is_valid_url(self, url):
        """Validate the URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except ValueError:
            return False
    
    def Ahmad_zip_folder(self, folder, zip_name):
        """Create ZIP file of downloaded website"""
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    filepath = os.path.join(root, file)
                    # Skip files that are too large
                    if os.path.getsize(filepath) > MAX_FILE_SIZE:
                        continue
                    arcname = os.path.relpath(filepath, folder)
                    zipf.write(filepath, arcname)
                    
    async def hmd_get_file_size(self, filename):
        """Get size of file in human-readable format"""
        size = os.path.getsize(filename)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    async def AHMD_cleanup(self, zip_path, folder_path):
        """Clean up downloaded files after delay"""
        await asyncio.sleep(180)  # 3 minutes
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                logger.info(f"Deleted ZIP file: {zip_path}")
            if os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                logger.info(f"Deleted folder: {folder_path}")
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            
    async def hmoudi_handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming URL messages"""
        user_id = update.effective_user.id
        chat_id = update.message.chat_id
        url = update.message.text.strip()
        
        # Validate URL
        if not self.hmd_is_valid_url(url):
            await update.message.reply_text("Please send a valid URL starting with http:// or https://")
            return
            
        # Check if user already has an active download
        if user_id in self.active_downloads:
            await update.message.reply_text("You already have a download in progress. Use /status to check progress.")
            return
            
        # Inform user that download is starting
        await update.message.reply_text("Starting website download... This may take a while depending on the site's size.")
        
        try:
            # Clear previous downloads
            self.downloader.downloaded_urls = set()
            
            # Download the website
            self.active_downloads[user_id] = "Download in progress..."
            total_size = self.downloader.hmoudi_download_website(url, DOWNLOAD_FOLDER)
            
            # Check if anything was downloaded
            if not os.path.exists(DOWNLOAD_FOLDER) or not os.listdir(DOWNLOAD_FOLDER):
                await update.message.reply_text("Failed to download any content from the website. It might be blocking automated access.")
                if user_id in self.active_downloads:
                    del self.active_downloads[user_id]
                return
            
            # Create ZIP file
            self.active_downloads[user_id] = "Creating ZIP archive"
            self.Ahmad_zip_folder(DOWNLOAD_FOLDER, ZIP_FILE_NAME)
            
            # Check if ZIP file was created and get its size
            if not os.path.exists(ZIP_FILE_NAME):
                await update.message.reply_text("Failed to create ZIP file.")
                if user_id in self.active_downloads:
                    del self.active_downloads[user_id]
                return
                
            zip_size = await self.hmd_get_file_size(ZIP_FILE_NAME)
            
            # Send the ZIP file
            self.active_downloads[user_id] = "Sending file to user"
            await update.message.reply_text(f"Download completed! Downloaded {len(self.downloader.downloaded_urls)} resources. File size: {zip_size}. Sending now...")
            
            with open(ZIP_FILE_NAME, 'rb') as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=f"Here's your downloaded website: {url}",
                    filename=f"website_backup_{urlparse(url).netloc}.zip"
                )
            
            # Schedule cleanup
            asyncio.create_task(self.AHMD_cleanup(ZIP_FILE_NAME, DOWNLOAD_FOLDER))
            
            # Remove user from active downloads
            if user_id in self.active_downloads:
                del self.active_downloads[user_id]
                
            await update.message.reply_text("File sent successfully! Files will be automatically deleted in 3 minutes.")
            
        except Exception as e:
            logger.error(f"Error processing website download: {e}")
            await update.message.reply_text(f"An error occurred while processing your request: {str(e)}")
            
            # Clean up on error
            if user_id in self.active_downloads:
                del self.active_downloads[user_id]
            if os.path.exists(ZIP_FILE_NAME):
                os.remove(ZIP_FILE_NAME)
            if os.path.exists(DOWNLOAD_FOLDER):
                import shutil
                shutil.rmtree(DOWNLOAD_FOLDER)
    
    def hmd_run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        self.app.run_polling()

if __name__ == '__main__':
    # Install required packages if not already installed
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        import requests
        from bs4 import BeautifulSoup
        
    bot = WebsiteDownloaderBot()
    bot.hmd_run()