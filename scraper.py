import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

DEFAULT_TOKENS = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "TRX"]

def get_top_tokens(limit: int = 20) -> list[str]:
    """
    Scrape the CoinMarketCap homepage to get the top tokens displayed.
    
    Args:
        limit: Maximum number of tokens to retrieve (default: 20)
    
    Returns:
        List of token symbols (e.g., ['BTC', 'ETH', 'USDT', ...])
    """
    try:
        logger.info(f"Fetching top {limit} tokens from CoinMarketCap...")
        
        url = "https://coinmarketcap.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        symbols = []
        seen_urls = set()
        
        # Find all links to /currencies/<coin>/ (not #markets or other anchors)
        links = soup.find_all('a', href=lambda x: x and x.startswith('/currencies/') and x.endswith('/') and '#' not in x)
        
        for link in links:
            href = link.get('href')

            # Skip if we've already seen this coin URL
            if href in seen_urls:
                continue
            seen_urls.add(href)
            
            full_text = link.get_text(strip=True)
            
            # Pattern: "FullNameSYMBOL" where SYMBOL is uppercase 2-10 chars
            # But sometimes it's "FullNameSYMBOLSYMBOL" (duplicated)
            match = re.search(r'([A-Z0-9]{1,10})$', full_text)
            
            if match:
                symbol = match.group(1)
                
                # Check if the symbol appears twice at the end (e.g., "BNBBNB" → "BNB")
                # Only apply when len > 5 to avoid incorrectly halving real symbols like "ABAB"
                if len(symbol) > 5 and len(symbol) % 2 == 0:
                    half = len(symbol) // 2
                    if symbol[:half] == symbol[half:]:
                        symbol = symbol[:half]
                
                # Filter out common false positives and very long "symbols"
                if 2 <= len(symbol) <= 6 and symbol not in symbols:
                    symbols.append(symbol)
                    if len(symbols) >= limit:
                        break
        
        logger.info(f"Found {len(symbols)} tokens: {symbols[:10]}{'...' if len(symbols) > 10 else ''}")
        return symbols[:limit]
        
    except requests.RequestException as e:
        logger.error(f"Error fetching data from CoinMarketCap: {e}")
        # Return default tokens as fallback
        logger.warning("Using default tokens as fallback")
        return DEFAULT_TOKENS
    except Exception as e:
        logger.error(f"Unexpected error while scraping: {e}")
        return DEFAULT_TOKENS


if __name__ == "__main__":
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    tokens = get_top_tokens(20)
    print(f"Top 20 tokens: {tokens}")
