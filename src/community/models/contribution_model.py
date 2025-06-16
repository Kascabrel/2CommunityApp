from enum import Enum
from community.models import db


class ContributionStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    RECEIVED = "RECEIVED"


class ContributionRun(db.Model):
    __tablename__ = "contribution_runs"
    id = db.Column(db.Integer, primary_key=True)
    number_of_members = db.Column(db.Integer, nullable=False)  # nombre total de membres dans la session
    minimal_contribution = db.Column(db.Float, nullable=False)  # montant minimal par part
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # facultatif au début

    # Relation vers UserContributionRun (association utilisateurs → session avec nombre de parts)
    user_contributions = db.relationship("UserContributionRun", back_populates="contribution_run")

    # Relation vers les contributions mensuelles (les versements réels)
    contributions = db.relationship("Contribution", back_populates="contribution_run")


class UserContributionRun(db.Model):
    __tablename__ = "user_contribution_runs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contribution_run_id = db.Column(db.Integer, db.ForeignKey("contribution_runs.id"), nullable=False)

    number_of_parts = db.Column(db.Integer, nullable=False,
                                default=1)  # combien de parts ce user prend dans cette session

    user = db.relationship("User", back_populates="user_contribution_runs")
    contribution_run = db.relationship("ContributionRun", back_populates="user_contributions")

    __table_args__ = (
        db.UniqueConstraint("user_id", "contribution_run_id", name="uq_user_contribution_run"),
    )


class Contribution(db.Model):
    __tablename__ = "contributions"
    id = db.Column(db.Integer, primary_key=True)

    contribution_run_id = db.Column(db.Integer, db.ForeignKey("contribution_runs.id"), nullable=False)
    user_contribution_run_id = db.Column(db.Integer, db.ForeignKey("user_contribution_runs.id"), nullable=False)

    month = db.Column(db.Date, nullable=False)  # par ex, 1er du mois
    amount = db.Column(db.Float, nullable=False)  # montant versé ce mois pour cette part
    status = db.Column(db.Enum(ContributionStatus), default=ContributionStatus.PENDING, nullable=False)

    winner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # gagnant ce mois

    contribution_run = db.relationship("ContributionRun", back_populates="contributions")
    user_contribution_run = db.relationship("UserContributionRun")
    winner_user = db.relationship("User", foreign_keys=[winner_user_id], back_populates='won_contributions')

    user_monthly_contributions = db.relationship('UserMonthlyContribution', back_populates='contribution')


class PaymentStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class UserMonthlyContribution(db.Model):
    __tablename__ = 'user_monthly_contributions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contribution_id = db.Column(db.Integer, db.ForeignKey('contributions.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_date = db.Column(db.Date, nullable=True)  # optionnel: date à laquelle le paiement a été fait

    user = db.relationship('User', back_populates='monthly_contributions')
    contribution = db.relationship('Contribution', back_populates='user_monthly_contributions')

    def __repr__(self):
        return f'<UserMonthlyContribution user_id={self.user_id} contribution_id={self.contribution_id} amount={self.amount} status={self.status}>'
