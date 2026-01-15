from typing import List, Dict, Optional
from atlassian import Confluence
from bs4 import BeautifulSoup
import html2text
from app.utils.config import config
import re


class ConfluenceIngestionService:
    """Service for ingesting documents from Confluence"""
    
    def __init__(self, cloud: bool = None):
        """Initialize Confluence client
        
        Args:
            cloud: True for Confluence Cloud, False for Server/DC. 
                   Auto-detects if None based on URL (.atlassian.net = cloud)
        """
        config.validate_confluence()
        
        # Auto-detect cloud vs server based on URL
        if cloud is None:
            cloud = '.atlassian.net' in config.CONFLUENCE_URL or '.atlassian.com' in config.CONFLUENCE_URL
        
        # Clean URL - remove /wiki if present
        base_url = config.CONFLUENCE_URL.replace("/wiki", "").rstrip("/")
        
        # Use 'token' parameter for API tokens (not 'password')
        # This is the correct way for Confluence Cloud API tokens
        self.confluence = Confluence(
            url=base_url,
            username=config.CONFLUENCE_USERNAME,
            token=config.CONFLUENCE_API_TOKEN,  # Use 'token' for API tokens
            cloud=cloud
        )
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        # Use html2text for better conversion
        text = self.html_converter.handle(html_content)
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def get_page_content(self, page_id: str) -> Dict:
        """Get content of a specific Confluence page"""
        try:
            page = self.confluence.get_page_by_id(
                page_id,
                expand='body.storage,version,space'
            )
            
            # Extract text from HTML body
            html_body = page.get('body', {}).get('storage', {}).get('value', '')
            text_content = self.html_to_text(html_body)
            
            return {
                "id": page_id,
                "title": page.get('title', 'Untitled'),
                "content": text_content,
                "url": page.get('_links', {}).get('webui', ''),
                "space": page.get('space', {}).get('key', ''),
                "space_name": page.get('space', {}).get('name', ''),
                "version": page.get('version', {}).get('number', 1),
                "last_modified": page.get('version', {}).get('when', ''),
                "author": page.get('version', {}).get('by', {}).get('displayName', 'Unknown')
            }
        except Exception as e:
            raise Exception(f"Error fetching Confluence page {page_id}: {str(e)}")
    
    def search_pages(self, query: str = "", space_key: str = None, limit: int = 100) -> List[Dict]:
        """Search for pages in Confluence"""
        try:
            # Use CQL (Confluence Query Language) for search
            cql = f"text ~ \"{query}\"" if query else ""
            if space_key:
                cql = f"space = {space_key}" + (f" AND {cql}" if cql else "")
            
            results = self.confluence.cql(
                cql=cql or "order by lastModified desc",
                limit=limit,
                expand='space,version'
            )
            
            pages = []
            for result in results.get('results', []):
                page_info = {
                    "id": result.get('content', {}).get('id'),
                    "title": result.get('content', {}).get('title'),
                    "space": result.get('space', {}).get('key'),
                    "space_name": result.get('space', {}).get('name'),
                    "url": result.get('content', {}).get('_links', {}).get('webui', '')
                }
                pages.append(page_info)
            
            return pages
        except Exception as e:
            raise Exception(f"Error searching Confluence: {str(e)}")
    
    def get_all_pages_from_space(self, space_key: str, limit: int = 1000) -> List[Dict]:
        """Get all pages from a specific Confluence space"""
        try:
            # Use direct HTTP request instead of library (library has auth issues)
            import requests
            from requests.auth import HTTPBasicAuth
            
            base_url = config.CONFLUENCE_URL.replace("/wiki", "").rstrip("/")
            pages = []
            start = 0
            batch_size = 50
            
            while len(pages) < limit:
                # Use Confluence REST API to get pages
                api_url = f"{base_url}/wiki/rest/api/content"
                params = {
                    "spaceKey": space_key,
                    "start": start,
                    "limit": min(batch_size, limit - len(pages)),
                    "expand": "body.storage,version,space"
                }
                
                response = requests.get(
                    api_url,
                    auth=HTTPBasicAuth(config.CONFLUENCE_USERNAME, config.CONFLUENCE_API_TOKEN),
                    headers={'Accept': 'application/json'},
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    if response.status_code == 403:
                        raise Exception(f"403 FORBIDDEN - You don't have permission to access space '{space_key}'. Please check:\n1. Your account has access to this space in Confluence\n2. The space key is correct\n3. Your API token has the right permissions")
                    raise Exception(f"API returned status {response.status_code}: {response.text[:200]}")
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                for page in results:
                    html_body = page.get('body', {}).get('storage', {}).get('value', '')
                    text_content = self.html_to_text(html_body) if html_body else ''
                    
                    # Get web UI link
                    webui_link = page.get('_links', {}).get('webui', '')
                    if webui_link and not webui_link.startswith('http'):
                        webui_link = f"{base_url}/wiki{webui_link}"
                    
                    pages.append({
                        "id": page.get('id'),
                        "title": page.get('title', 'Untitled'),
                        "content": text_content,
                        "url": webui_link,
                        "space": space_key,
                        "space_name": page.get('space', {}).get('name', ''),
                        "version": page.get('version', {}).get('number', 1),
                        "last_modified": page.get('version', {}).get('when', ''),
                        "author": page.get('version', {}).get('by', {}).get('displayName', 'Unknown')
                    })
                
                if len(results) < batch_size:
                    break
                
                start += batch_size
                
                if len(pages) >= limit:
                    break
            
            return pages[:limit]
        except Exception as e:
            raise Exception(f"Error fetching pages from space {space_key}: {str(e)}")
    
    def get_all_spaces(self) -> List[Dict]:
        """Get all accessible Confluence spaces"""
        try:
            # Use direct HTTP request instead of library (library has auth issues)
            import requests
            from requests.auth import HTTPBasicAuth
            
            base_url = config.CONFLUENCE_URL.replace("/wiki", "").rstrip("/")
            api_url = f"{base_url}/wiki/rest/api/space"
            
            response = requests.get(
                api_url,
                auth=HTTPBasicAuth(config.CONFLUENCE_USERNAME, config.CONFLUENCE_API_TOKEN),
                headers={'Accept': 'application/json'},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text[:200]}")
            
            data = response.json()
            return [
                {
                    "key": space.get('key'),
                    "name": space.get('name'),
                    "type": space.get('type'),
                    "description": space.get('description', {}).get('plain', {}).get('value', '')
                }
                for space in data.get('results', [])
            ]
        except Exception as e:
            raise Exception(f"Error fetching Confluence spaces: {str(e)}")
    
    def ingest_space(self, space_key: str, limit: int = 1000) -> List[Dict]:
        """Ingest all pages from a Confluence space"""
        pages = self.get_all_pages_from_space(space_key, limit)
        
        ingested = []
        for page in pages:
            ingested.append({
                "source": "confluence",
                "page_id": page["id"],
                "title": page["title"],
                "content": page["content"],
                "url": page["url"],
                "space": page["space"],
                "space_name": page["space_name"],
                "author": page["author"],
                "last_modified": page["last_modified"],
                "metadata": {
                    "confluence_page_id": page["id"],
                    "confluence_url": page["url"],
                    "space_key": page["space"],
                    "version": page["version"]
                }
            })
        
        return ingested
    
    def ingest_all_spaces(self, limit_per_space: int = 1000) -> List[Dict]:
        """Ingest pages from all accessible Confluence spaces"""
        spaces = self.get_all_spaces()
        all_pages = []
        
        for space in spaces:
            space_key = space["key"]
            try:
                pages = self.ingest_space(space_key, limit_per_space)
                all_pages.extend(pages)
            except Exception as e:
                print(f"Error ingesting space {space_key}: {str(e)}")
                continue
        
        return all_pages
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap (same as DocumentIngestionService)"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def prepare_for_embedding(self, ingested_pages: List[Dict]) -> List[Dict]:
        """Prepare Confluence pages for embedding by chunking"""
        prepared = []
        
        for page in ingested_pages:
            chunks = self.chunk_text(page["content"])
            
            for i, chunk in enumerate(chunks):
                prepared.append({
                    "chunk_index": i,
                    "chunk": chunk,
                    "source": "confluence",
                    "page_id": page["page_id"],
                    "title": page["title"],
                    "url": page["url"],
                    "space": page["space"],
                    "space_name": page["space_name"],
                    "author": page["author"],
                    "metadata": page["metadata"]
                })
        
        return prepared
