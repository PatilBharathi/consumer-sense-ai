import requests
from bs4 import BeautifulSoup
import random

def scrape_url_text(url: str) -> str:
    """
    Fetches a URL and returns the clean visible text.
    Prioritizes 'Main Content' areas to avoid analyzing footers/nav bars.
    """
    # Robust User-Agent rotation
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. AGGRESSIVE CLEANING: Remove noise elements
        # We explicitly remove footers, navs, sidebars, and popups
        noise_selectors = [
            "script", "style", "header", "footer", "nav", "noscript", "iframe",
            ".footer", "#footer", ".nav", "#nav", ".navigation", 
            ".sidebar", "#sidebar", ".cookie-banner", ".ad-container",
            ".advertisement", ".menu", "#menu", ".search-bar"
        ]
        for selector in noise_selectors:
            for element in soup.select(selector):
                element.decompose() # Completely remove from tree

        # 2. SMART TARGETING: Try to find the "Meat" of the page
        # We look for common IDs/Classes for main content
        content_candidates = [
            # Amazon specific
            "#productDescription", "#feature-bullets", "#centerCol", 
            # News/Blog specific
            "article", "main", ".post-content", ".article-body", ".entry-content",
            "#content", ".content", ".main-content"
        ]
        
        extracted_text = ""
        
        # Try to find the best candidate
        for selector in content_candidates:
            element = soup.select_one(selector)
            if element:
                extracted_text = element.get_text(separator="\n")
                break # Stop once we find a good candidate
        
        # 3. FALLBACK: If no specific content area found, extract from Body (cleaned)
        if not extracted_text or len(extracted_text) < 100:
            body = soup.find("body")
            if body:
                extracted_text = body.get_text(separator="\n")
            
        # 4. CLEANUP: Normalize whitespace
        clean_lines = []
        for line in extracted_text.splitlines():
            stripped = line.strip()
            # Filter out short menu items or gibberish
            if len(stripped) > 3: 
                clean_lines.append(stripped)
                
        final_text = "\n".join(clean_lines)
        
        if len(final_text) < 50:
            return "Error: Unable to extract meaningful content. The site might be blocking access."

        return final_text[:15000]

    except Exception as e:
        print(f"Scrape Error: {e}")
        return ""