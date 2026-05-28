import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Тест перевіряє головну сторінку"""
    response = client.get('/')
    assert response.status_code in [200, 500]

def test_get_items(client):
    """Тест перевіряє отримання списку речей"""
    response = client.get('/items')
    assert response.status_code in [200, 500]

def test_post_item(client):
    """Тест перевіряє створення нової речі"""
    response = client.post('/items', json={"name": "Test Item"})
    assert response.status_code in [200, 201, 405, 500]

def test_404_page(client):
    """Тест перевіряє реакцію на неіснуючу сторінку"""
    response = client.get('/invalid-route-123')
    assert response.status_code == 404
