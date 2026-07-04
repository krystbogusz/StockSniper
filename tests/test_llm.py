import pytest
from unittest.mock import patch, MagicMock
from app.core import llm_client

def test_check_availability_found():
    mock_response = MagicMock()
    mock_response.text = '{"available_sizes": ["42"]}'
    
    with patch.object(llm_client.client.models, 'generate_content', return_value=mock_response):
        sizes = llm_client.check_availability("Przykładowy tekst strony", ["42", "44"])
        assert sizes == ["42"]

def test_check_availability_not_found():
    mock_response = MagicMock()
    mock_response.text = '{"available_sizes": []}'
    
    with patch.object(llm_client.client.models, 'generate_content', return_value=mock_response):
        sizes = llm_client.check_availability("Strona wyprzedana", ["42"])
        assert sizes == []

def test_check_url_safety_safe():
    mock_response = MagicMock()
    mock_response.text = '{"is_safe": true, "reason": "Bezpieczny sklep internetowy."}'
    
    with patch.object(llm_client.client.models, 'generate_content', return_value=mock_response):
        is_safe, reason = llm_client.check_url_safety("https://legit-shop.com")
        assert is_safe is True
        assert "Bezpieczny" in reason

def test_check_url_safety_unsafe():
    mock_response = MagicMock()
    mock_response.text = '{"is_safe": false, "reason": "Wykryto malware na stronie."}'
    
    with patch.object(llm_client.client.models, 'generate_content', return_value=mock_response):
        is_safe, reason = llm_client.check_url_safety("https://malware.com")
        assert is_safe is False
        assert "malware" in reason
