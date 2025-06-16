from flask import Blueprint, request, jsonify
from datetime import datetime
from community.controllers.contribution_controller import ContributionController
from community.models import db  # Tu dois avoir une session SQLAlchemy ici

contribution_bp = Blueprint('contribution', __name__, url_prefix='/contribution')
controller = ContributionController(db.session)


@contribution_bp.route('/session', methods=['POST'])
def create_contribution_session():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    number_of_members = data.get('number_of_members')
    minimal_contribution = data.get('minimal_contribution')
    start_date = data.get('start_date')

    missing_fields = [field for field in ['number_of_members', 'minimal_contribution', 'start_date'] if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        session = controller.create_session(number_of_members, minimal_contribution, start_date)
        return jsonify({"message": "Session created", "session_id": session.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/session/<int:session_id>/add-user', methods=['POST'])
def add_user_to_contribution_session(session_id):
    data = request.get_json()
    user_id = data.get('user_id')
    number_of_parts = data.get('number_of_parts', 1)

    if not user_id:
        return jsonify({"error": "user_id requis"}), 400

    try:
        uc = controller.add_user_to_session(session_id, user_id, number_of_parts)
        return jsonify({"message": "Utilisateur ajouté", "user_contribution_id": uc.id, "user_id": uc.user_id }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/session/<int:session_id>/generate-months', methods=['POST'])
def generate_monthly_contributions(session_id):
    try:
        controller.generate_monthly_contributions(session_id)
        return jsonify({"message": "Cotisations mensuelles générées"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/payment/<int:user_monthly_contrib_id>', methods=['POST'])
def record_payment(user_monthly_contrib_id):
    data = request.get_json()
    payment_date = data.get('payment_date')  # Optionnel

    try:
        if payment_date:
            payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
        result = controller.record_payment(user_monthly_contrib_id, payment_date)
        return jsonify({
            "message": "Paiement enregistré",
            "payment_id": result.id,
            "status": result.status.name
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/contribution/<int:contribution_id>/winner', methods=['POST'])
def set_contribution_winner(contribution_id):
    data = request.get_json()
    winner_user_id = data.get('winner_user_id')

    if not winner_user_id:
        return jsonify({"error": "winner_user_id requis"}), 400

    try:
        contribution = controller.set_month_winner(contribution_id, winner_user_id)
        return jsonify({
            "message": "Gagnant défini",
            "contribution_id": contribution.id,
            "status": contribution.status.name
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/sessions', methods=['GET'])
def list_all_sessions():
    sessions = controller.list_sessions()
    return jsonify([
        {
            "id": s.id,
            "minimal_contribution": s.minimal_contribution,
            "start_date": s.start_date.isoformat(),
            "number_of_members": s.number_of_members
        } for s in sessions
    ])


@contribution_bp.route('/session/<int:session_id>/contributions', methods=['GET'])
def get_session_contributions(session_id):
    contributions = controller.get_session_contributions(session_id)
    return jsonify([
        {
            "id": c.id,
            "month": c.month.isoformat(),
            "amount": c.amount,
            "status": c.status.name,
            "user_id": c.user_contribution.user_id
        } for c in contributions
    ])


@contribution_bp.route('/user/<int:user_id>/payments', methods=['GET'])
def get_user_payments(user_id):
    payments = controller.get_user_payments(user_id)
    return jsonify([
        {
            "id": p.id,
            "amount": p.amount,
            "status": p.status.name,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "contribution_id": p.contribution_id
        } for p in payments
    ])
