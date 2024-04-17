# cases/models.py

from app import db
from datetime import datetime
from sqlalchemy.orm import relationship  # Import relationship from SQLAlchemy


class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    dependent_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    case_amount = db.Column(db.Float, nullable=True)
    closed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='open')
    closed_at = db.Column(db.DateTime, nullable=True)
    contributions = db.relationship('Contribution', back_populates='case', lazy=True)
    # Define a one-to-many relationship with Expense model
    expenses = relationship("Expense", backref="case", lazy="dynamic")

    def __init__(self, member_id, dependent_id=None, case_amount=0.0):
        self.member_id = member_id
        self.dependent_id = dependent_id
        self.created_at = datetime.utcnow()
        self.case_amount = case_amount

    @classmethod
    def create_case(cls, member_id, dependent_id=None, case_amount=0.0):
        case = cls(member_id=member_id, dependent_id=dependent_id, case_amount=case_amount)
        db.session.add(case)
        db.session.commit()
        return case

    @classmethod
    def get_case(cls, case_id):
        return cls.query.get(case_id)
    
    @classmethod
    def get_cases(cls):
        return cls.query.all()
    
    @classmethod
    def get_member_cases(cls, member_id):
        return cls.query.filter_by(member_id=member_id).all()
    
    @classmethod
    def get_deceased_cases(cls, dependent_id):
        return cls.query.filter_by(dependent_id=dependent_id).all()
    
    @classmethod
    def get_member_deceased_cases(cls, member_id, dependent_id):
        return cls.query.filter_by(member_id=member_id, dependent_id=dependent_id).all()
    
    @classmethod
    def delete_case(cls, case_id):
        case = cls.query.get(case_id)
        db.session.delete(case)
        db.session.commit()

    def __repr__(self):
        return "<Case: {}>".format(self.id)
    
    def serialize(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'dependent_id': self.dependent_id,
            'member_deceased': self.member_deceased,
            'created_at': self.created_at,
            'case_amount': self.case_amount
        }
    
    def close_case(self):
        self.closed = True
        self.closed_at = datetime.utcnow()
        db.session.commit()
        return self
