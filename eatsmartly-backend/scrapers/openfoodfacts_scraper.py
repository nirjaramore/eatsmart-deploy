"""
Open Food Facts — search + product details via public API (no HTML scraping).
Reliable fallback when Amazon.in / BigBasket block or return nothing.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# Regional mirrors — some networks reach one host better than others
OFF_SEARCH_URLS = [
    "https://world.openfoodfacts.org/cgi/search.pl",
    "https://in.openfoodfacts.org/cgi/search.pl",
    "https://us.openfoodfacts.org/cgi/search.pl",
]
OFF_PRODUCT_API = "https://world.openfoodfacts.org/api/v0/product"


def relevance_score(title: str, query: str) -> float:
    if not title or not query:
        return 0.0
    q_words = {w for w in re.findall(r"\w+", query.lower()) if len(w) > 1}
    t_words = {w for w in re.findall(r"\w+", title.lower()) if len(w) > 1}
    if not q_words:
        return 0.0
    return len(q_words & t_words) / len(q_words)


def _off_headers() -> Dict[str, str]:
    # Non-browser UAs often get HTML error pages → JSON decode fails → 0 products
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json,text/javascript,*/*;q=0.1",
        "Accept-Language": "en-IN,en;q=0.9",
    }


def search_open_food_facts(product_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search OFF using the classic search API (better relevance than blind v2 for short queries).
    """
    if not (product_name or "").strip():
        return []
    try:
        logger.info(f"🔍 Open Food Facts search: {product_name!r}")
        params = {
            "search_terms": product_name.strip(),
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": min(max(max_results * 3, 10), 30),
        }
        r = None
        data = None
        last_err = None
        for search_url in OFF_SEARCH_URLS:
            try:
                r = requests.get(
                    search_url,
                    params=params,
                    headers=_off_headers(),
                    timeout=(8, 45),
                )
                if r.status_code != 200:
                    logger.warning(f"OFF search HTTP {r.status_code} ({search_url})")
                    continue
                try:
                    data = r.json()
                except ValueError as je:
                    snippet = (r.text or "")[:400].replace("\n", " ")
                    logger.warning(
                        f"OFF search returned non-JSON from {search_url}: {je!s}; body[:400]={snippet!r}"
                    )
                    last_err = je
                    continue
                raw_try = data.get("products") if isinstance(data, dict) else None
                if raw_try is not None:
                    break
            except requests.RequestException as e:
                logger.warning(f"OFF search request failed ({search_url}): {e}")
                last_err = e
                continue
        if data is None or not isinstance(data, dict):
            if last_err:
                logger.error(f"Open Food Facts: all mirrors failed; last error: {last_err}")
            return []
        raw = data.get("products") or []
        out: List[Dict[str, Any]] = []
        for p in raw:
            code = (p.get("code") or "").strip()
            if not code:
                continue
            name = p.get("product_name") or p.get("product_name_en") or p.get("generic_name") or ""
            if not name:
                continue
            brands = p.get("brands") or ""
            img = (
                p.get("image_front_small_url")
                or p.get("image_front_url")
                or p.get("image_url")
            )
            rel = relevance_score(name, product_name)
            product_url = f"https://world.openfoodfacts.org/product/{code}"
            out.append(
                {
                    "source": "Open Food Facts",
                    "product_name": name.strip(),
                    "brand": brands.strip() if isinstance(brands, str) else None,
                    "price": None,
                    "rating": None,
                    "image_url": img,
                    "product_url": product_url,
                    "code": code,
                    "confidence": 0.55 + 0.35 * min(rel, 1.0),
                }
            )
        out.sort(
            key=lambda x: (relevance_score(x.get("product_name") or "", product_name), x.get("confidence", 0)),
            reverse=True,
        )
        return out[:max_results]
    except requests.Timeout:
        logger.error("Open Food Facts search timed out")
        return []
    except Exception as e:
        logger.error(f"Open Food Facts search error: {e}")
        return []


def _code_from_openfoodfacts_url(product_url: str) -> Optional[str]:
    m = re.search(r"openfoodfacts\.org/product/(\d{8,14})", product_url, re.I)
    return m.group(1) if m else None


def _map_nutriments(n: Dict[str, Any]) -> Dict[str, Any]:
    """Map OFF nutriments to keys expected by the website (`buildParsedFromScraperProduct`)."""
    nutrition: Dict[str, Any] = {}
    if not n:
        return nutrition

    def f(key: str) -> Optional[float]:
        v = n.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    cal = f("energy-kcal_100g") or f("energy-kcal")
    if cal is None and f("energy_100g") is not None:
        # energy in kJ → kcal rough
        try:
            nutrition["calories"] = round(float(n["energy_100g"]) / 4.184, 1)
        except (TypeError, ValueError):
            pass
    else:
        if cal is not None:
            nutrition["calories"] = cal

    p = f("proteins_100g") or f("proteins")
    if p is not None:
        nutrition["protein"] = p
    fat = f("fat_100g") or f("fat")
    if fat is not None:
        nutrition["totalFat"] = fat
    carbs = f("carbohydrates_100g") or f("carbohydrates")
    if carbs is not None:
        nutrition["carbs"] = carbs
    sug = f("sugars_100g") or f("sugars")
    if sug is not None:
        nutrition["sugars"] = sug
    fib = f("fiber_100g") or f("fiber")
    if fib is not None:
        nutrition["fiber"] = fib
    sod = f("sodium_100g") or f("sodium")
    if sod is not None:
        nutrition["sodium"] = sod
    return nutrition


def get_open_food_facts_product_details(product_url: str) -> Optional[Dict[str, Any]]:
    code = _code_from_openfoodfacts_url(product_url)
    if not code:
        logger.warning(f"Could not parse OFF barcode from URL: {product_url}")
        return None
    try:
        url = f"{OFF_PRODUCT_API}/{code}.json"
        r = requests.get(url, headers=_off_headers(), timeout=(5, 20))
        if r.status_code != 200:
            return None
        j = r.json()
        if not j or j.get("status") != 1:
            return None
        prod = j.get("product") or {}
        n = prod.get("nutriments") or {}
        nutrition = _map_nutriments(n)

        img = prod.get("image_front_url") or prod.get("image_url")
        name = prod.get("product_name") or prod.get("product_name_en") or "Unknown product"
        brand = prod.get("brands")
        if isinstance(brand, str):
            brand = brand.split(",")[0].strip() or None

        ingredients = prod.get("ingredients_text") or prod.get("ingredients_text_en")
        features: List[str] = []
        if ingredients:
            features.append(f"Ingredients: {ingredients[:500]}{'…' if len(str(ingredients)) > 500 else ''}")

        return {
            "source": "Open Food Facts",
            "product_name": name,
            "brand": brand,
            "image_url": img,
            "price": None,
            "rating": None,
            "description": prod.get("generic_name") or prod.get("product_name"),
            "features": features,
            "specifications": {
                "countries": prod.get("countries"),
                "quantity": prod.get("quantity"),
                "nutriscore": prod.get("nutrition_grade_fr") or prod.get("nutriscore_grade"),
            },
            "nutrition": nutrition if nutrition else None,
            "product_url": f"https://world.openfoodfacts.org/product/{code}",
        }
    except Exception as e:
        logger.error(f"OFF product API error: {e}")
        return None
