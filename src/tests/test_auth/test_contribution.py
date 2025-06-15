import pytest
from datetime import datetime

from src import create_app, db
from src.models.user_model import UserRole


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_contribution_session(client):
    response = client.post('/contribution/session', json={
        'number_of_members': 3,
        'minimal_contribution': 100,
        'start_date': datetime.utcnow().date().isoformat()
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'session_id' in data


def test_create_contribution_session_missing_fields(client):
    response = client.post('/contribution/session', json={
        'minimal_contribution': 100
        # missing number_of_member and start_date
    })
    assert response.status_code == 400
    assert 'Missing required fields' in response.get_json().get('error', '')


def test_add_user_to_session(client):
    # D'abord, créer une session
    resp1 = client.post('/contribution/session', json={
        'number_of_members': 2,
        'minimal_contribution': 50,
        'start_date': datetime.utcnow().date().isoformat()
    })
    session_id = resp1.get_json()['session_id']

    # Créer un utilisateur (via endpoint auth/register par ex. ou directement en base ici)
    # Pour simplifier, ajout direct en DB ici
    from src.models.user_model import User
    from src import db as _db

    # register a new user
    client.post('auth/register', json={
        'first_name': 'steve',
        'last_name': 'Doe',
        'email': 'jean@steve.com',
        'password': 'password123'
    })
    user_email = "jean@steve.com"
    response = client.get(f'auth/get_id/{user_email}')
    assert response.status_code == 200
    user_id = response.get_json()['user_id']
    # Ajouter user à session
    print(f"the session id is: {session_id}")
    resp2 = client.post(f'/contribution/session/{session_id}/add-user', json={
        'session_id': session_id,
        'user_id': user_id,
        'number_of_parts': 1
    })
    assert resp2.status_code == 201
    data = resp2.get_json()
    assert data['user_id'] == user_id


def test_generate_monthly_contributions(client):
    # Setup session + user
    resp1 = client.post('/contribution/contribution', json={
        'number_of_member': 1,
        'minimal_contribution': 100,
        'start_date': datetime.utcnow().date().isoformat()
    })
    session_id = resp1.get_json()['id']

    from src.models.user_model import User
    from src import db as _db

    user = User(email="user2@example.com", name="User Two")
    with client.application.app_context():
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id

    # Add user to session
    client.post('/contribution/add_user', json={
        'session_id': session_id,
        'user_id': user_id,
        'number_of_parts': 2
    })

    # Generate monthly contributions
    resp2 = client.post('/contribution/generate_monthly_contributions', json={'session_id': session_id})
    assert resp2.status_code == 200
    assert 'message' in resp2.get_json()


def test_record_payment(client):
    # Setup session + user + contribution + user_monthly_contribution manually or call endpoints
    # Pour test rapide, créer session, user, ajouter user, générer contributions

    resp1 = client.post('/contribution/session', json={
        'number_of_members': 1,
        'minimal_contribution': 100,
        'start_date': datetime.utcnow().date().isoformat()
    })
    session_id = resp1.get_json()['session_id']

    client.post('auth/register', json={
        'first_name': 'User',
        'last_name': 'Three',
        'email': "user3@example.com",
        'password': 'password123'
    })
    user_email = "user3@example.com"
    response = client.get(f'auth/get_id/{user_email}')
    assert response.status_code == 200
    user_id = response.get_json()['user_id']

    client.post(f'/contribution/session/{session_id}/add-user', json={
        'session_id': session_id,
        'user_id': user_id,
        'number_of_parts': 1
    })

    client.post(f'/contribution/session/{session_id}/generate_months')

    # Récupérer un UserMonthlyContribution
    from src.models.contribution_model import UserMonthlyContribution
    with client.application.app_context():
        umc = UserMonthlyContribution.query.filter_by(user_id=user_id).first()
        print(f"the received object is: {umc}")
        umc_id = umc.id

    # Enregistrer paiement
    resp2 = client.post('/contribution/record_payment', json={'user_monthly_contrib_id': umc_id})
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert data['status'] == 'PAID'


def test_set_month_winner(client):
    # Setup contribution and user like before

    resp1 = client.post('/contribution/contribution', json={
        'number_of_member': 1,
        'minimal_contribution': 100,
        'start_date': datetime.utcnow().date().isoformat()
    })
    session_id = resp1.get_json()['id']

    from src.models.user_model import User
    from src import db as _db

    user = User(email="user4@example.com", name="User Four")
    with client.application.app_context():
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id

    client.post('/contribution/add_user', json={
        'session_id': session_id,
        'user_id': user_id,
        'number_of_parts': 1
    })

    client.post('/contribution/generate_monthly_contributions', json={'session_id': session_id})

    from src.models.contribution_model import Contribution
    with client.application.app_context():
        contrib = Contribution.query.filter_by(contribution_run_id=session_id).first()
        contrib_id = contrib.id

    resp2 = client.post('/contribution/set_winner', json={
        'contribution_id': contrib_id,
        'winner_user_id': user_id
    })
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert data['winner_user_id'] == user_id
