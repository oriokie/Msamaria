from app import db
from sqlalchemy.orm import relationship

class RegistrationFee(db.Model):
    __tablename__ = 'registration_fees'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.Date, nullable=False)

    member = db.relationship('Member', backref='registration_fees')

    def __repr__(self):
        return f"<RegistrationFee {self.amount} for member {self.member_id}>"
    
    @staticmethod
    def get_total_registration_fees():
        return RegistrationFee.query.with_entities(db.func.sum(RegistrationFee.amount)).scalar() or 0
