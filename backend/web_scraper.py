"""
Web scraper for relevant Bible commentary and data.
"""

import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class BibleWebScraper:
    """Scrape web for relevant Bible commentary and data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.timeout = 10
        self.delay = 1  # Delay between requests
    
    def search_bible_commentary(
        self,
        passage: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for Bible commentary on the web."""
        results = []
        
        # Search multiple sources
        search_queries = [
            f"{passage} commentary",
            f"{passage} bible study",
            f"{passage} exegesis",
        ]
        
        for query in search_queries[:2]:  # Limit to avoid too many requests
            try:
                # Search Google (using a simple approach)
                # Note: For production, use official APIs
                search_results = self._search_google(query, max_results=3)
                results.extend(search_results)
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error searching for {query}: {e}")
                continue
        
        # Also try specific Bible commentary sites
        commentary_sites = self._get_commentary_sites(passage)
        sites_tried = 0
        for site_url in commentary_sites:
            if sites_tried >= 3:  # Limit to 3 successful sites
                break
            try:
                content = self._scrape_commentary_site(site_url, passage)
                if content and len(content.strip()) > 100:  # Only add if substantial content
                    results.append({
                        "source": urlparse(site_url).netloc,
                        "url": site_url,
                        "content": content,
                        "type": "commentary"
                    })
                    sites_tried += 1
                time.sleep(self.delay)
            except Exception as e:
                # Silently skip 404s and other errors - try next site
                if "404" not in str(e):
                    print(f"Warning: Error scraping {site_url}: {e}")
                continue
        
        return results[:max_results]
    
    def _search_google(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search Google for Bible commentary (simplified approach)."""
        # Note: This is a simplified implementation
        # For production, use Google Custom Search API or similar
        
        # Try to get search results from DuckDuckGo (more permissive)
        try:
            return self._search_duckduckgo(query, max_results)
        except Exception:
            # Fallback: return empty or use cached/predefined sources
            return []
    
    def _search_duckduckgo(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search DuckDuckGo for Bible commentary."""
        results = []
        
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find result links
            result_links = soup.find_all('a', class_='result__a', limit=max_results)
            
            for link in result_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Skip if not a Bible/commentary related site
                if not self._is_relevant_site(href):
                    continue
                
                # Try to scrape the page
                try:
                    content = self._scrape_page_content(href)
                    if content:
                        results.append({
                            "source": urlparse(href).netloc,
                            "url": href,
                            "title": title,
                            "content": content[:2000],  # Limit content
                            "type": "web"
                        })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return results
    
    def _get_commentary_sites(self, passage: str) -> List[str]:
        """Get URLs for known Bible commentary sites."""
        book, chapter, verse_range = self._parse_passage(passage)
        
        # Try multiple URL patterns for each site
        sites = []
        
        # BibleStudyTools - try different patterns
        sites.extend([
            f"https://www.biblestudytools.com/commentaries/{book.lower()}/{chapter}/",
            f"https://www.biblestudytools.com/{book.lower()}/{chapter}/",
        ])
        
        # BibleHub - more reliable pattern
        sites.extend([
            f"https://biblehub.com/commentaries/{book.lower()}/{chapter}.htm",
            f"https://biblehub.com/{book.lower()}/{chapter}.htm",
        ])
        
        # StudyLight
        sites.extend([
            f"https://www.studylight.org/commentaries/{book.lower()}/{chapter}.html",
            f"https://www.studylight.org/commentaries/eng/{book.lower()}/{chapter}.html",
        ])
        
        # BlueLetterBible
        sites.append(f"https://www.blueletterbible.org/comm/{book.lower()}/{chapter}")
        
        return sites
    
    def _scrape_commentary_site(self, url: str, passage: str) -> Optional[str]:
        """Scrape content from a commentary site."""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            # Don't raise on 404 - just return None
            if response.status_code == 404:
                return None
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                'article',
                '.content',
                '.commentary',
                '.main-content',
                'main',
                '#content',
                '.post-content'
            ]
            
            content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator='\n', strip=True)
                    break
            
            if not content:
                # Fallback: get body text
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            # Clean up content
            if content:
                content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                return content[:3000]  # Limit length
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
        return None
    
    def _scrape_page_content(self, url: str) -> Optional[str]:
        """Scrape main content from a web page."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Find main content
            main_content = (
                soup.find('article') or
                soup.find('main') or
                soup.select_one('.content, .post-content, .entry-content, #content')
            )
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                # Clean up
                text = re.sub(r'\n{3,}', '\n\n', text)
                return text[:2000]  # Limit length
            
        except Exception:
            pass
        
        return None
    
    def _is_relevant_site(self, url: str) -> bool:
        """Check if URL is from a relevant Bible/commentary site."""
        relevant_domains = [
            'biblestudytools.com',
            'biblehub.com',
            'studylight.org',
            'biblegateway.com',
            'blueletterbible.org',
            'gotquestions.org',
            'desiringgod.org',
            'ligonier.org',
            'thegospelcoalition.org',
            'crossway.org',
        ]
        
        domain = urlparse(url).netloc.lower()
        return any(rel in domain for rel in relevant_domains)
    
    def _parse_passage(self, passage: str) -> tuple:
        """Parse Bible passage into book, chapter, verse."""
        match = re.match(r"(\w+)\s+(\d+)(?::(\d+(?:-\d+)?))?", passage)
        if match:
            return match.group(1), int(match.group(2)), match.group(3) or ""
        return "", 0, ""
    
    def get_relevant_data_for_passage(
        self,
        passage: str,
        max_web_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Get all relevant web data for a passage."""
        return self.search_bible_commentary(passage, max_results=max_web_results)
