from datetime import datetime, timedelta
from src import db
from src.models.contribution_model import ContributionRun, UserContributionRun, Contribution, ContributionStatus, \
    UserMonthlyContribution, PaymentStatus
from src.models.user_model import User

"""
Explications :
create_session() : Crée une nouvelle session de cotisation.
add_user_to_session() : Ajoute un utilisateur à une session, avec nombre de parts.
generate_monthly_contributions() : Crée toutes les contributions mensuelles ainsi que les entrées de paiement individuelles (UserMonthlyContribution) à partir des parts et du montant minimal.
record_payment() : Marque un paiement manuel comme effectué, avec date (IBAN).
set_month_winner() : Désigne le gagnant du mois pour une contribution spécifique.
Méthodes pour lister sessions, cotisations, paiements pour faciliter l’affichage dans le dashboard."""


class ContributionController:
    @staticmethod
    def create_session(number_of_members: int, minimal_contribution: float,
                       start_date: datetime.date) -> ContributionRun:
        session = ContributionRun(
            number_of_members=number_of_members,
            minimal_contribution=minimal_contribution,
            start_date=start_date
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def add_user_to_session(session_id: int, user_id: int, number_of_parts: int = 1) -> UserContributionRun:
        # Vérifie que la session existe
        session = ContributionRun.query.get(session_id)
        if not session:
            raise ValueError("Session non trouvée")

        # Vérifie que l'utilisateur existe
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Ajoute l'utilisateur à la session
        user_contrib = UserContributionRun(
            user_id=user_id,
            contribution_run_id=session_id,
            number_of_parts=number_of_parts
        )
        db.session.add(user_contrib)
        db.session.commit()
        return user_contrib

    @staticmethod
    def generate_monthly_contributions(session_id: int) -> None:
        session = ContributionRun.query.get(session_id)
        if not session:
            raise ValueError("Session non trouvée")

        # Durée = somme des parts des utilisateurs (exemple simple)
        total_parts = sum(uc.number_of_parts for uc in session.user_contributions)
        months_duration = total_parts

        # Pour chaque mois, générer les contributions par utilisateur
        for month_index in range(months_duration):
            contribution_month = session.start_date + timedelta(days=30 * month_index)

            for user_contrib in session.user_contributions:
                amount = user_contrib.number_of_parts * session.minimal_contribution

                # Crée une contribution mensuelle
                contribution = Contribution(
                    contribution_run_id=session.id,
                    user_contribution_run_id=user_contrib.id,
                    month=contribution_month,
                    amount=amount,
                    status=ContributionStatus.PENDING
                )
                db.session.add(contribution)

                # Crée l'entrée de paiement par utilisateur
                user_monthly_contrib = UserMonthlyContribution(
                    user_id=user_contrib.user_id,
                    contribution=contribution,
                    amount=amount,
                    status=PaymentStatus.PENDING
                )
                db.session.add(user_monthly_contrib)

        db.session.commit()

    @staticmethod
    def record_payment(user_monthly_contrib_id: int, payment_date: datetime.date = None) -> UserMonthlyContribution:
        # Enregistre le paiement manuel reçu (ex : par IBAN) pour une contribution utilisateur
        payment = UserMonthlyContribution.query.get(user_monthly_contrib_id)
        if not payment:
            raise ValueError("Paiement non trouvé")

        payment.status = PaymentStatus.PAID
        payment.payment_date = payment_date or datetime.utcnow().date()

        # Vérifie si tous les paiements liés à cette contribution sont réglés
        contribution = payment.contribution
        unpaid = [u for u in contribution.user_monthly_contributions if u.status != PaymentStatus.PAID]
        if not unpaid:
            contribution.status = ContributionStatus.PAID

        db.session.commit()
        return payment

    @staticmethod
    def set_month_winner(contribution_id: int, winner_user_id: int) -> Contribution:
        contribution = Contribution.query.get(contribution_id)
        if not contribution:
            raise ValueError("Contribution non trouvée")

        # Vérifie que l'utilisateur gagnant appartient à la session
        session_user_ids = [uc.user_id for uc in contribution.contribution_run.user_contributions]
        if winner_user_id not in session_user_ids:
            raise ValueError("Utilisateur gagnant ne fait pas partie de la session")

        contribution.winner_user_id = winner_user_id
        contribution.status = ContributionStatus.RECEIVED  # marque comme "reçu" par le gagnant

        db.session.commit()
        return contribution

    @staticmethod
    def list_sessions():
        return ContributionRun.query.all()

    @staticmethod
    def get_session_contributions(session_id: int):
        return Contribution.query.filter_by(contribution_run_id=session_id).all()

    @staticmethod
    def get_user_payments(user_id: int):
        return UserMonthlyContribution.query.filter_by(user_id=user_id).all()
