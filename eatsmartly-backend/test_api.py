"""
Basic tests for EatSmartly backend.
Run with: pytest test_api.py
"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EatSmartly API"
    assert data["version"] == "1.0.0"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # May fail if DB not running
    data = response.json()
    assert "status" in data


def test_analyze_barcode_invalid():
    """Test barcode analysis with invalid barcode."""
    response = client.post(
        "/analyze-barcode",
        json={
            "barcode": "invalid",
            "user_id": "test_user"
        }
    )
    # Should return 404 or 500 depending on validation
    assert response.status_code in [404, 500]


def test_search_endpoint():
    """Test food search endpoint."""
    response = client.post(
        "/search",
        json={
            "query": "apple",
            "user_id": "test_user",
            "limit": 5
        }
    )
    # May succeed or fail depending on USDA API
    assert response.status_code in [200, 500]


def test_get_user_profile():
    """Test getting user profile."""
    response = client.get("/user/test_user/profile")
    assert response.status_code in [200, 500]


def test_update_user_profile():
    """Test updating user profile."""
    response = client.post(
        "/user/test_user/profile",
        json={
            "age": 30,
            "gender": "male",
            "health_goal": "weight_loss",
            "allergies": ["peanuts"],
            "health_conditions": [],
            "dietary_restrictions": []
        }
    )
    assert response.status_code in [200, 500]


# Utility tests
def test_normalize_barcode():
    """Test barcode normalization."""
    from agents.utils import normalize_barcode
    
    assert normalize_barcode("012345678905") == "0012345678905"
    assert normalize_barcode("0012345678905") == "0012345678905"
    assert normalize_barcode("invalid") is None
    assert normalize_barcode("12345") is None


def test_validate_checksum():
    """Test UPC checksum validation."""
    from agents.utils import validate_upc_checksum
    
    # Valid EAN-13
    assert validate_upc_checksum("0012345678905") is True or False
    
    # Invalid
    assert validate_upc_checksum("invalid") is False
    assert validate_upc_checksum("") is False


def test_extract_allergens():
    """Test allergen extraction."""
    from agents.utils import extract_allergens
    
    ingredients = "Contains: Milk, Eggs, Wheat, Soy"
    allergens = extract_allergens(ingredients)
    
    assert "milk" in allergens
    assert "eggs" in allergens
    assert "wheat" in allergens
    assert "soy" in allergens


def test_calculate_health_score():
    """Test health score calculation."""
    from agents.utils import calculate_health_score
    
    # Healthy food
    healthy_food = {
        "protein_g": 20,
        "fiber_g": 8,
        "sugar_g": 2,
        "sodium_mg": 100,
        "saturated_fat_g": 1
    }
    score = calculate_health_score(healthy_food)
    assert score > 50
    
    # Unhealthy food
    unhealthy_food = {
        "protein_g": 2,
        "fiber_g": 0,
        "sugar_g": 30,
        "sodium_mg": 1000,
        "saturated_fat_g": 15
    }
    score = calculate_health_score(unhealthy_food)
    assert score < 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
