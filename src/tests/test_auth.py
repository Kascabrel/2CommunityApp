import pytest

from src import create_app, db


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_register_with_email(client):
    response = client.post('auth/register', json={
        'first_name': 'steve',
        'last_name': 'Doe',
        'email': 'jean@steve.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.get_json() == {"message": "User registered successfully"}


def test_register_duplicate_email(client):
    # first registration
    client.post('auth/register', json={
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jean@example.com",
        "password": "123456"
    })

    # second registration with the same email
    response = client.post('auth/register', json={
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jean@example.com",  # même email
        "password": "123456"
    })

    assert response.status_code == 409
    assert "Email already registered" in response.get_json()["error"]


def test_register_missing_field(client):
    response = client.post('auth/register', json={
        "first_name": "Jean",
        "email": "jean@example.com",
        "password": "123456"
    })  # last_name is missing

    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]


def test_register_with_admin_role(client):
    response = client.post('auth/register', json={
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'jean@example.com',
        'password': 'admin123',
        'role': 'admin'
    })
    assert response.status_code == 400
    assert "Invalid admin identifier" in response.get_json()["error"]
