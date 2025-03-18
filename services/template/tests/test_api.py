import json
import pytest
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from app.models import db, Item

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        db.create_all()
    
    yield flask_app
    
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'template'

def test_create_item(client):
    # Test creating a new item
    response = client.post(
        '/api/items',
        data=json.dumps({'name': 'Test Item', 'description': 'This is a test item'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Item'
    assert data['description'] == 'This is a test item'

def test_get_items(client):
    # Create a test item
    client.post(
        '/api/items',
        data=json.dumps({'name': 'Test Item', 'description': 'This is a test item'}),
        content_type='application/json'
    )
    
    # Test getting all items
    response = client.get('/api/items')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['name'] == 'Test Item'

def test_get_item(client):
    # Create a test item
    response = client.post(
        '/api/items',
        data=json.dumps({'name': 'Test Item', 'description': 'This is a test item'}),
        content_type='application/json'
    )
    item_id = json.loads(response.data)['id']
    
    # Test getting the item by ID
    response = client.get(f'/api/items/{item_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Item'
    assert data['id'] == item_id

def test_update_item(client):
    # Create a test item
    response = client.post(
        '/api/items',
        data=json.dumps({'name': 'Test Item', 'description': 'This is a test item'}),
        content_type='application/json'
    )
    item_id = json.loads(response.data)['id']
    
    # Test updating the item
    response = client.put(
        f'/api/items/{item_id}',
        data=json.dumps({'name': 'Updated Item', 'description': 'This item has been updated'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Item'
    assert data['description'] == 'This item has been updated'

def test_delete_item(client):
    # Create a test item
    response = client.post(
        '/api/items',
        data=json.dumps({'name': 'Test Item', 'description': 'This is a test item'}),
        content_type='application/json'
    )
    item_id = json.loads(response.data)['id']
    
    # Test deleting the item
    response = client.delete(f'/api/items/{item_id}')
    assert response.status_code == 200
    
    # Verify the item is gone
    response = client.get(f'/api/items/{item_id}')
    assert response.status_code == 404 