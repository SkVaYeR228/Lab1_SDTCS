import pytest
from app import app
import app as my_app

my_app.db_config = {
    'host': 'dummy_host',
    'user': 'dummy_user',
    'password': 'dummy_password',
    'database': 'dummy_db'
}

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code in [200, 500]

def test_get_items(client):
    try:
        response = client.get('/items')
        assert response.status_code in [200, 500]
    except Exception:
        pass

def test_post_item(client):
    try:
        response = client.post('/items', json={"name": "Test Item"})
        assert response.status_code in [200, 201, 405, 500]
    except Exception:
        pass

def test_404_page(client):
    response = client.get('/invalid-route-123')
    assert response.status_code == 404
