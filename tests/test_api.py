import pytest
from unittest.mock import patch

from app.core.config import settings


def test_docs_auth_failure(client):
    response = client.get("/docs")
    assert response.status_code == 401


def test_docs_auth_success(client):
    response = client.get("/docs", auth=(settings.api_username, settings.api_password))
    assert response.status_code == 200


def test_api_unauthorized_access(client):
    response = client.get("/item/list")
    assert response.status_code == 401


def test_item_add_success(client, auth_headers):
    with patch("app.api.endpoints.item.check_url_safety", return_value=(True, "Safe")):
        payload = {
            "url": "https://test.com/shoes",
            "size": "42",
            "interval_value": 5,
            "interval_unit": "minutes",
        }
        response = client.post("/item/add", json=payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["success"] is True


def test_item_add_unsafe_url(client, auth_headers):
    with patch(
        "app.api.endpoints.item.check_url_safety",
        return_value=(False, "Phishing site detected"),
    ):
        payload = {
            "url": "https://malicious.com/shoes",
            "size": "42",
            "interval_value": 5,
            "interval_unit": "minutes",
        }
        response = client.post("/item/add", json=payload, headers=auth_headers)
        assert response.status_code == 400
        assert "URL rejected" in response.json()["detail"]


def test_item_add_invalid_interval(client, auth_headers):
    payload = {
        "url": "https://test.com/shoes",
        "size": "42",
        "interval_value": 10,
        "interval_unit": "seconds",
    }
    response = client.post("/item/add", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_item_list(client, auth_headers):
    response = client.get("/item/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_item_delete(client, auth_headers):
    with patch("app.api.endpoints.item.check_url_safety", return_value=(True, "Safe")):
        client.post(
            "/item/add",
            json={
                "url": "https://test.com/delete-me",
                "size": "L",
                "interval_value": 1,
                "interval_unit": "hours",
            },
            headers=auth_headers,
        )

    payload = {
        "url": "https://test.com/delete-me",
        "size": "L",
        "interval_value": 1,
        "interval_unit": "hours",
    }
    response = client.post("/item/delete", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_settings_toggle_logging(client, auth_headers):
    # Test enabling logging
    response = client.post(
        "/settings/logging", json={"enabled": True}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "enabled" in response.json()["message"]

    # Test disabling logging
    response = client.post(
        "/settings/logging", json={"enabled": False}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "disabled" in response.json()["message"]
