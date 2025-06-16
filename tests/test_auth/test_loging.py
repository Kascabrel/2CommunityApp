import pytest


@pytest.fixture
def client():
    from community import create_app
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            # Ici, tu peux créer les tables et insérer un utilisateur de test
            from community.models import db
            from community.models.user_model import User, UserRole
            db.create_all()

            # Création d'un utilisateur test
            salt = "testsalt"
            user = User(
                firstname="Test",
                lastname="User",
                email="testuser@example.com",
                salt=salt,
                role=UserRole.USER
            )
            user.set_password("correct_password", salt)
            db.session.add(user)
            db.session.commit()
        yield client
        db.session.remove()
        db.drop_all()


def test_login_success(client):
    # Test login avec les bonnes infos
    response = client.post('/auth/login', json={
        "email": "testuser@example.com",
        "password": "correct_password"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_wrong_password(client):
    # Test avec mauvais mot de passe
    response = client.post('/auth/login', json={
        "email": "testuser@example.com",
        "password": "wrong_password"
    })
    data = response.get_json()
    assert response.status_code == 401
    assert data["error"] == "Invalid credentials"


def test_login_nonexistent_email(client):
    # Test avec email non enregistré
    response = client.post('/auth/login', json={
        "email": "doesnotexist@example.com",
        "password": "whatever"
    })
    data = response.get_json()
    assert response.status_code == 401
    assert data["error"] == "Invalid credentials"


def test_login_missing_fields(client):
    # Test avec champs manquants
    response = client.post('/auth/login', json={
        "email": "testuser@example.com"
        # missing password
    })
    data = response.get_json()
    assert response.status_code == 400
    assert "Email and password required" in data["error"]


def test_login_invalid_email_format(client):
    # Test avec format email invalide
    response = client.post('/auth/login', json={
        "email": "invalid-email-format",
        "password": "whatever"
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data["error"] == "Invalid email format"


def test_login_missing_json(client):
    # Test sans JSON dans la requête
    response = client.post('/auth/login', json= {})
    data = response.get_json()
    assert response.status_code == 400
    assert data["error"] == "Missing JSON body"
