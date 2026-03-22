"""
Amazon India Product Scraper
Searches Amazon.in for products and extracts nutrition information
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Rotate user agents to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
]

# ASIN: 10 alphanumeric (Amazon standard)
_ASIN_RE = re.compile(r'^[A-Z0-9]{10}$')


def get_headers():
    """Get randomized headers for requests"""
    import random
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-IN,en;q=0.9,hi;q=0.8',
        # Omit br: some Python stacks mishandle Brotli and Amazon HTML becomes unusable
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://www.amazon.in/',
        'Cache-Control': 'no-cache',
    }


def _is_bot_or_captcha_html(html: str) -> bool:
    h = html.lower()
    return any(
        x in h
        for x in (
            'api-services-support@amazon',
            'enter the characters you see below',
            'robot check',
            'sorry, we just need to make sure you',
            'type the characters in the image',
        )
    )


def _title_from_result_card(card) -> Optional[str]:
    """Amazon changes inner markup often; try several patterns."""
    selectors = [
        'h2 a span.a-text-normal',
        'h2 a .a-text-normal',
        'h2 span.a-text-normal',
        'a.a-link-normal span.a-text-normal',
        'h2 a span',
        'h2 span',
        'span.a-size-medium.a-color-base.a-text-normal',
        'span.a-size-base-plus.a-color-base.a-text-normal',
        '.a-size-medium.a-color-base',
    ]
    for sel in selectors:
        el = card.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and len(t) > 3:
                return t
    h2 = card.find('h2')
    if h2:
        t = h2.get_text(strip=True)
        if t and len(t) > 3:
            return t
    return None


def _price_from_card(card) -> Optional[float]:
    off = card.select_one('span.a-price span.a-offscreen')
    if off:
        m = re.search(r'[\d,]+(?:\.\d+)?', off.get_text(strip=True).replace(',', ''))
        if m:
            try:
                return float(m.group(0).replace(',', ''))
            except ValueError:
                pass
    whole = card.find('span', class_='a-price-whole')
    if whole:
        try:
            return float(whole.get_text(strip=True).replace(',', ''))
        except ValueError:
            pass
    return None


def _relevance_score(title: str, query: str) -> float:
    """Rough token overlap so the closest title to the user's query ranks first."""
    if not title or not query:
        return 0.0
    q_words = {w for w in re.findall(r'\w+', query.lower()) if len(w) > 1}
    t_words = {w for w in re.findall(r'\w+', title.lower()) if len(w) > 1}
    if not q_words:
        return 0.0
    inter = len(q_words & t_words)
    return inter / len(q_words)


def _collect_search_cards(soup: BeautifulSoup, max_results: int) -> List:
    """Amazon SERP markup varies; try primary then fallback selectors."""
    cards = soup.find_all('div', {'data-component-type': 's-search-result'})
    if cards:
        logger.info(f"Using s-search-result cards: {len(cards)}")
        return cards[: max_results * 2]

    cards = soup.select('div[data-asin][data-index]')
    if cards:
        logger.info(f"Using div[data-asin][data-index] cards: {len(cards)}")
        return cards[: max_results * 2]

    # Last resort: any block with a real ASIN + product title pattern
    seen_asin = set()
    out = []
    for div in soup.find_all('div', attrs={'data-asin': True}):
        asin = (div.get('data-asin') or '').strip().upper()
        if not _ASIN_RE.match(asin) or asin in seen_asin:
            continue
        if div.get('data-component-type') == 'sp-sponsored-result':
            continue
        if not _title_from_result_card(div):
            continue
        seen_asin.add(asin)
        out.append(div)
        if len(out) >= max_results * 2:
            break
    if out:
        logger.info(f"Using fallback data-asin cards: {len(out)}")
    return out

def search_amazon_india(product_name: str, max_results: int = 5) -> List[Dict]:
    """
    Search Amazon India for products matching the given name
    
    Args:
        product_name: Name of product to search for
        max_results: Maximum number of results to return (default 5)
        
    Returns:
        List of product dictionaries with basic info
    """
    try:
        logger.info(f"🔍 Searching Amazon India for: {product_name}")
        
        search_url = f"https://www.amazon.in/s?k={quote_plus(product_name.strip())}"
        
        response = requests.get(
            search_url,
            headers=get_headers(),
            timeout=15
        )
        
        if response.status_code != 200:
            logger.warning(f"Amazon returned status code: {response.status_code}")
            return []
        
        raw = response.text
        if _is_bot_or_captcha_html(raw):
            logger.warning(
                "Amazon returned a bot-check or captcha page (no product list). "
                "Try again later, use a residential IP, or reduce request rate."
            )
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        product_cards = _collect_search_cards(soup, max_results)
        logger.info(f"Found {len(product_cards)} candidate product cards on Amazon")
        
        products: List[Dict] = []
        seen_asin = set()
        
        for card in product_cards:
            if len(products) >= max_results:
                break
            try:
                asin = (card.get('data-asin') or '').strip().upper()
                if not _ASIN_RE.match(asin):
                    sub = card.select_one('[data-asin]')
                    if sub and sub.get('data-asin'):
                        asin = sub.get('data-asin').strip().upper()
                if not _ASIN_RE.match(asin) or asin in seen_asin:
                    continue
                
                title = _title_from_result_card(card)
                if not title:
                    continue
                
                seen_asin.add(asin)
                price = _price_from_card(card)
                
                rating = None
                rating_elem = card.find('span', class_='a-icon-alt')
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    match = re.search(r'(\d+\.?\d*)', rating_text)
                    if match:
                        try:
                            rating = float(match.group(1))
                        except ValueError:
                            pass
                
                img_elem = card.find('img', class_='s-image') or card.find('img', src=re.compile(r'images-amazon'))
                image_url = img_elem.get('src') if img_elem else None
                
                product_url = f"https://www.amazon.in/dp/{asin}"
                
                brand = None
                brand_elem = card.find('span', class_='a-size-base-plus')
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
                
                products.append({
                    'source': 'Amazon India',
                    'product_name': title,
                    'brand': brand,
                    'price': price,
                    'rating': rating,
                    'image_url': image_url,
                    'product_url': product_url,
                    'asin': asin,
                    'confidence': 0.8
                })
                
                logger.info(f"✅ Found: {title[:50]}... (₹{price if price else 'N/A'})")
                
            except Exception as e:
                logger.error(f"Error parsing product card: {e}")
                continue
        
        products.sort(
            key=lambda p: (_relevance_score(p.get('product_name') or '', product_name), p.get('confidence', 0)),
            reverse=True,
        )
        logger.info(f"✅ Returning {len(products)} products from Amazon India")
        return products
        
    except requests.exceptions.Timeout:
        logger.error("Amazon request timed out")
        return []
    except Exception as e:
        logger.error(f"Error searching Amazon India: {e}")
        return []

def get_amazon_product_details(product_url: str) -> Optional[Dict]:
    """
    Get detailed product information from Amazon product page
    
    Args:
        product_url: Full URL to Amazon product page
        
    Returns:
        Dictionary with detailed product info including nutrition
    """
    try:
        logger.info(f"📦 Getting Amazon product details from: {product_url}")
        
        # Add rate limiting to be polite
        time.sleep(1)
        
        response = requests.get(
            product_url,
            headers=get_headers(),
            timeout=15
        )
        
        if response.status_code != 200:
            logger.warning(f"Amazon returned status code: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract product title
        title_elem = soup.find('span', id='productTitle')
        product_name = title_elem.get_text(strip=True) if title_elem else None
        
        # Extract brand
        brand_elem = soup.find('a', id='bylineInfo')
        if not brand_elem:
            brand_elem = soup.find('span', class_='a-size-base po-break-word')
        brand = None
        if brand_elem:
            brand_text = brand_elem.get_text(strip=True)
            brand = brand_text.replace('Visit the ', '').replace(' Store', '').strip()
        
        # Extract image
        image_elem = soup.find('img', id='landingImage')
        if not image_elem:
            image_elem = soup.find('img', class_='a-dynamic-image')
        image_url = image_elem.get('src') if image_elem else None
        
        # Extract price
        price_elem = soup.find('span', class_='a-price-whole')
        price = None
        if price_elem:
            try:
                price = float(price_elem.get_text(strip=True).replace(',', ''))
            except ValueError:
                pass
        
        # Extract rating
        rating_elem = soup.find('span', class_='a-icon-alt')
        rating = None
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                try:
                    rating = float(match.group(1))
                except ValueError:
                    pass
        
        # Extract description
        desc_elem = soup.find('div', id='productDescription')
        description = None
        if desc_elem:
            desc_p = desc_elem.find('p')
            if desc_p:
                description = desc_p.get_text(strip=True)
        
        # Extract features (bullet points)
        features = []
        feature_div = soup.find('div', id='feature-bullets')
        if feature_div:
            feature_items = feature_div.find_all('span', class_='a-list-item')
            for item in feature_items:
                feature_text = item.get_text(strip=True)
                if feature_text and len(feature_text) > 10:  # Skip empty/short items
                    features.append(feature_text)
        
        # Extract specifications
        specifications = {}
        spec_table = soup.find('table', id='productDetails_techSpec_section_1')
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    specifications[key] = value
        
        # Extract nutrition information (CRITICAL FOR YOUR APP!)
        nutrition = extract_nutrition_from_page(soup)
        
        product_details = {
            'source': 'Amazon India',
            'product_name': product_name,
            'brand': brand,
            'image_url': image_url,
            'price': price,
            'rating': rating,
            'description': description,
            'features': features,
            'specifications': specifications,
            'nutrition': nutrition,
            'product_url': product_url
        }
        
        logger.info(f"✅ Extracted details for: {product_name}")
        if nutrition:
            logger.info(f"✅ Found nutrition info: {list(nutrition.keys())}")
        
        return product_details
        
    except requests.exceptions.Timeout:
        logger.error("Amazon product page request timed out")
        return None
    except Exception as e:
        logger.error(f"Error getting Amazon product details: {e}")
        return None

def extract_nutrition_from_page(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Extract nutrition information from Amazon product page
    
    Args:
        soup: BeautifulSoup object of product page
        
    Returns:
        Dictionary with nutrition values or None
    """
    nutrition = {}
    
    try:
        # Look for nutrition tables in various sections
        sections_to_check = [
            soup.find('div', id='important-information'),
            soup.find('div', id='productDescription'),
            soup.find('div', class_='a-section content')
        ]
        
        for section in sections_to_check:
            if not section:
                continue
            
            # Look for text containing nutrition keywords
            section_text = section.get_text().lower()
            
            # Check if this section contains nutrition info
            if not any(keyword in section_text for keyword in ['nutrition', 'energy', 'protein', 'carbohydrate']):
                continue
            
            # Try to extract from table
            tables = section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value_text = cells[1].get_text(strip=True)
                        
                        # Extract numeric value
                        match = re.search(r'(\d+\.?\d*)', value_text)
                        if match:
                            try:
                                value = float(match.group(1))
                                
                                # Map to standard nutrition keys
                                if 'energy' in key or 'calor' in key:
                                    nutrition['calories'] = value
                                elif 'protein' in key:
                                    nutrition['protein'] = value
                                elif 'fat' in key and 'saturated' not in key:
                                    nutrition['totalFat'] = value
                                elif 'saturated' in key:
                                    nutrition['saturatedFat'] = value
                                elif 'carbohydrate' in key or 'carbs' in key:
                                    nutrition['carbs'] = value
                                elif 'sugar' in key:
                                    nutrition['sugars'] = value
                                elif 'fiber' in key or 'fibre' in key:
                                    nutrition['fiber'] = value
                                elif 'sodium' in key or 'salt' in key:
                                    nutrition['sodium'] = value
                                    
                            except ValueError:
                                continue
            
            # If found nutrition info in this section, break
            if nutrition:
                break
        
        return nutrition if nutrition else None
        
    except Exception as e:
        logger.error(f"Error extracting nutrition: {e}")
        return None
