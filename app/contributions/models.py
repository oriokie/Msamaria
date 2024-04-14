from app import db
from sqlalchemy.orm import relationship
from app.cases.models import Case


class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    
    # Define relationship with Member and Case models
    member = relationship("Member", back_populates="contributions")
    case = relationship("Case", back_populates="contributions")

    def __repr__(self):
        return f"Contribution(member_id={self.member_id}, case_id={self.case_id}, paid={self.paid})"
    
    @classmethod
    def create_contribution(cls, member_id, case_id):
        contribution = cls(member_id=member_id, case_id=case_id)
        db.session.add(contribution)
        db.session.commit()
        return contribution
    
    @classmethod
    def bulk_mark_as_paid(cls, member_id, case_id):
        contribution = cls.query.filter_by(member_id=member_id, case_id=case_id).first()
        if contribution:  # Check if a contribution is found
            contribution.paid = True
            db.session.commit()
        else:
            # Handle case where no contribution is found for the member and case_id
            print(f'No contribution found for member {member_id} and case {case_id}')
        return contribution  # Consider returning the updated contribution object


    @classmethod
    def get_contributions(cls):
        return cls.query.all()
    
    @classmethod
    def get_member_contributions(cls, member_id):
        return cls.query.filter_by(member_id=member_id).all()
    
    @classmethod
    def get_case_contributions(cls, case_id):
        return cls.query.filter_by(case_id=case_id).all()
    
    @classmethod
    def get_contribution(cls, contribution_id):
        return cls.query.get(contribution_id)
    
    @classmethod
    def delete_contribution(cls, contribution_id):
        contribution = cls.query.get(contribution_id)
        db.session.delete(contribution)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'case_id': self.case_id,
            'paid': self.paid
        }
    
    def mark_as_paid(self):
        self.paid = True
        db.session.commit()
        return self.serialize()
    
    def mark_as_unpaid(self):
        self.paid = False
        db.session.commit()
        return self.serialize()