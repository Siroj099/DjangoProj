import pytest
from unittest.mock import patch
from django.core.cache import cache
from django.urls import reverse
from tests.create_tests.factories import TicketFactory

@pytest.mark.django_db
def test_valid_request(client):
    ticket1 = TicketFactory(title="Mock ticket 1")
    ticket2 = TicketFactory(title="Useless ticket 2")

    url = reverse("search_tickets")
    params = {"query": "Mock", "page": 1}  # Searching this data
    
    headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    cache.clear()
    
    # To mock web page and not waste resources
    with patch("django.template.loader.render_to_string", return_value="<div>Mocked HTML</div>"):
        response = client.get(url, params, **headers)

    assert response.status_code == 200
    json_data = response.json()
    
    # Tests to verify search correctness
    assert json_data["success"] is True
    assert "html" in json_data
    assert json_data["count"] == 1
    assert json_data["pagination"]["current_page"] == 1
    assert json_data["pagination"]["total_pages"] == 1
    assert json_data["pagination"]["has_next"] is False
    assert json_data["pagination"]["has_previous"] is False

@pytest.mark.django_db
def test_search_tickets_pagination(client):
    TicketFactory.create_batch(15, title="random tickets")
    url = reverse("search_tickets")
    headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    
    with patch("django.template.loader.render_to_string", return_value="<div>Mocked HTML</div>"):
        response = client.get(url, {"query": "random", "page": 2}, **headers)

    assert response.status_code == 200
    json_data = response.json()

    # Test to verify correctness of pagination
    assert json_data["pagination"]["current_page"] == 2
    assert json_data["pagination"]["has_next"] is False
    assert json_data["pagination"]["has_previous"] is True

@pytest.mark.django_db
def test_search_tickets_cache(client):
    TicketFactory(title="Cached Ticket")

    url = reverse("search_tickets")
    headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    with patch("django.template.loader.render_to_string", return_value="<div>Mocked HTML</div>"):
        response = client.get(url, {"query": "Cached"}, **headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True

    cache_key = "search_tickets_Cached_1"
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert cached_data["success"] is True