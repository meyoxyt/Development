"""Web and HTTP tools"""

import aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WebTools:
    """HTTP requests and web scraping"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
    
    async def http_request(self, url: str, method: str = "GET", data: dict = None) -> str:
        """Make HTTP request"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status = response.status
                    headers = dict(response.headers)
                    content = await response.text()
                    
                    result = [
                        f"Status: {status}",
                        f"Content-Length: {len(content)}",
                        f"Content-Type: {headers.get('Content-Type', 'unknown')}",
                        "",
                        "Response:",
                        content[:5000]  # Limit output
                    ]
                    
                    if len(content) > 5000:
                        result.append(f"\n... truncated ({len(content)} total bytes)")
                    
                    logger.info(f"HTTP {method} {url} -> {status}")
                    return "\n".join(result)
                    
        except Exception as e:
            logger.error(f"HTTP request error: {e}")
            return f"Error: {str(e)}"
    
    async def download_file(self, url: str, path: str) -> str:
        """Download file from URL"""
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = self.workspace / file_path
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    size = file_path.stat().st_size
                    logger.info(f"Downloaded {url} to {path} ({size} bytes)")
                    return f"Successfully downloaded {size} bytes to {path}"
                    
        except Exception as e:
            logger.error(f"Download error: {e}")
            return f"Error: {str(e)}"
    
    async def scrape_webpage(self, url: str) -> str:
        """Extract content from webpage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Extract title
                    title = soup.title.string if soup.title else "No title"
                    
                    # Remove script and style elements
                    for element in soup(['script', 'style', 'nav', 'footer']):
                        element.decompose()
                    
                    # Get text content
                    text = soup.get_text(separator='\n', strip=True)
                    
                    # Clean up whitespace
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    content = '\n'.join(lines)
                    
                    result = [
                        f"Title: {title}",
                        f"URL: {url}",
                        "",
                        "Content:",
                        content[:5000]
                    ]
                    
                    if len(content) > 5000:
                        result.append(f"\n... truncated ({len(content)} total chars)")
                    
                    logger.info(f"Scraped {url}")
                    return "\n".join(result)
                    
        except Exception as e:
            logger.error(f"Scrape error: {e}")
            return f"Error: {str(e)}"
