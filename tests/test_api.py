import pytest
from app import create_app
import json

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "MONGO_URI": "mongodb://localhost:27017/blog_test_db"
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    """Test the base API route (Frontend)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Stellar" in response.data

def test_signup_validation(client):
    """Test signup with missing data."""
    response = client.post('/api/auth/signup', 
                           data=json.dumps({"username": "testuser"}),
                           content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json

def test_unauthorized_blog_creation(client):
    """Ensure non-authors cannot create blogs."""
    response = client.post('/api/blogs/', 
                           data=json.dumps({"title": "Hack", "content": "Test"}),
                           content_type='application/json')
    assert response.status_code == 401 # Missing token

def test_get_all_blogs(client):
    """Test retrieving the blog list."""
    response = client.get('/api/blogs/')
    assert response.status_code == 200
    assert 'blogs' in response.json

def test_search_no_query(client):
    """Test search endpoint without query parameter."""
    response = client.get('/api/blogs/search')
    assert response.status_code == 400
    assert 'error' in response.json

def test_get_comments_empty(client):
    """Test getting comments for a non-existent blog."""
    # Using a valid-format but non-existent ObjectId
    fake_id = '507f1f77bcf86cd799439011'
    response = client.get(f'/api/comments/blog/{fake_id}')
    assert response.status_code == 200
    assert response.json['comments'] == []
