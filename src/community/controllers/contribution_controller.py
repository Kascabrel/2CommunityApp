from datetime import datetime, timedelta

from flask import jsonify

from community.models.contribution_model import (
    ContributionRun,
    UserContributionRun,
    Contribution,
    ContributionStatus,
    UserMonthlyContribution,
    PaymentStatus
)
from community.models.user_model import User
from sqlalchemy.orm import Session
from typing import List, Optional


class ContributionController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_session(
            self,
            number_of_members: int,
            minimal_contribution: float,
            start_date: datetime.date
    ) -> ContributionRun:
        session = ContributionRun(
            number_of_members=number_of_members,
            minimal_contribution=minimal_contribution,
            start_date=start_date
        )
        self.db_session.add(session)
        self.db_session.commit()
        return session

    def add_user_to_session(
            self,
            session_id: int,
            user_id: int,
            number_of_parts: int = 1
    ) -> UserContributionRun:
        session = self.db_session.get(ContributionRun, session_id)
        if not session:
            raise ValueError("Session non trouvée")

        user = self.db_session.get(User, user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")

        user_contrib = UserContributionRun(
            user_id=user_id,
            contribution_run_id=session_id,
            number_of_parts=number_of_parts
        )
        self.db_session.add(user_contrib)
        self.db_session.commit()
        return user_contrib

    def generate_monthly_contributions(self, session_id: int) -> None:
        session = self.db_session.get(ContributionRun, session_id)
        if not session:
            raise ValueError("Session not found")

        total_parts = sum(uc.number_of_parts for uc in session.user_contributions)
        months_duration = total_parts
        for month_index in range(months_duration):
            contribution_month = session.start_date + timedelta(days=30 * month_index)

            for user_contrib in session.user_contributions:
                amount = user_contrib.number_of_parts * session.minimal_contribution

                contribution = Contribution(
                    contribution_run_id=session.id,
                    user_contribution_run_id=user_contrib.id,
                    month=contribution_month,
                    amount=amount,
                    status=ContributionStatus.PENDING
                )
                self.db_session.add(contribution)

                user_monthly_contrib = UserMonthlyContribution(
                    user_id=user_contrib.user_id,
                    contribution=contribution,
                    amount=amount,
                    status=PaymentStatus.PENDING
                )
                self.db_session.add(user_monthly_contrib)

        self.db_session.commit()


    def record_payment(
            self,
            user_monthly_contrib_id: int,
            payment_date: Optional[datetime.date] = None
    ) -> UserMonthlyContribution:
        payment = self.db_session.get(UserMonthlyContribution, user_monthly_contrib_id)
        if not payment:
            raise ValueError("Paiement non trouvé")

        payment.status = PaymentStatus.PAID
        payment.payment_date = payment_date or datetime.utcnow().date()

        contribution = payment.contribution
        unpaid = [
            u for u in contribution.user_monthly_contributions
            if u.status != PaymentStatus.PAID
        ]
        if not unpaid:
            contribution.status = ContributionStatus.PAID

        self.db_session.commit()
        return payment

    def set_month_winner(self, contribution_id: int, winner_user_id: int) -> Contribution:
        contribution = self.db_session.get(Contribution, contribution_id)
        if not contribution:
            raise ValueError("Contribution non trouvée")

        session_user_ids = [
            uc.user_id for uc in contribution.contribution_run.user_contributions
        ]
        if winner_user_id not in session_user_ids:
            raise ValueError("Utilisateur gagnant ne fait pas partie de la session")

        contribution.winner_user_id = winner_user_id
        contribution.status = ContributionStatus.RECEIVED

        self.db_session.commit()
        return contribution

    def list_sessions(self) -> List[ContributionRun]:
        return self.db_session.query(ContributionRun).all()

    def get_session_contributions(self, session_id: int) -> List[Contribution]:
        return self.db_session.query(Contribution).filter_by(
            contribution_run_id=session_id
        ).all()

    def get_user_payments(self, user_id: int) -> List[UserMonthlyContribution]:
        return self.db_session.query(UserMonthlyContribution).filter_by(
            user_id=user_id
        ).all()

    def get_all_user_monthly_contribution(self):
        """ this method will only be use for testcase with pytest"""
        user_list = self.db_session.query(UserMonthlyContribution).all()
        if not user_list:
            return None
        return [user.user_id for user in user_list]
