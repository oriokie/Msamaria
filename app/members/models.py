#This is the members model

from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.orm import relationship  # Import relationship from SQLAlchemy
from app.dependents.models import Dependent
from app.cases.models import Case
from app.contributions.models import Contribution
from sqlalchemy import desc



class Member(UserMixin, db.Model):
    """This class represents the members table."""
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    id_number = db.Column(db.String(12), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    reg_fee_paid = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    is_deceased = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    dependents = db.relationship('Dependent', backref='member', lazy=True)
    cases = db.relationship('Case', backref='member', lazy=True)
    contributions = db.relationship('Contribution', back_populates='member', lazy=True)
    
    
    def __init__(self, name, id_number, phone_number, password):
        self.name = name
        self.id_number = id_number
        self.phone_number = phone_number
        self.set_password(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Member: {}>".format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def serialize(self, include_dependents=False):
        serialized_member = {
            'id': self.id,
            'name': self.name,
            'id_number': self.id_number,
            'phone_number': self.phone_number,
            'reg_fee_paid': self.reg_fee_paid,
            'is_admin': self.is_admin,
            'active': self.active,
            'is_deceased': self.is_deceased,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }

        # Optionally include dependents
        if include_dependents:
            serialized_member['dependents'] = [dependent.serialize() for dependent in self.dependents]

        return serialized_member


    def activate(self):
        self.active = True
        db.session.commit()
    
    def deactivate(self):
        self.active = False
        db.session.commit()
    
    def make_admin(self):
        self.is_admin = True
        db.session.commit()

    def remove_admin(self):
        self.is_admin = False
        db.session.commit()

    def pay_reg_fee(self):
        self.reg_fee_paid = True
        db.session.commit()

    def mark_deceased(self):
        self.is_deceased = True
        db.session.commit()

    def mark_alive(self):
        self.is_deceased = False
        db.session.commit()
    
    def get_id(self):
        return self.id
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    @staticmethod
    def create_first_admin():
        # Check if an admin already exists
        #admin = Member.query.filter_by(is_admin=True).first()
        #if admin:
            #print("Admin already exists.")
            #return admin

        # If admin doesn't exist, create one
        try:
            admin = Member(name="Admin", id_number="8888888888", phone_number="0700000000", password="admin")
            admin.make_admin()
            admin.activate()
            admin.is_authenticated = True
            admin.reg_fee_paid = True
            db.session.add(admin)
            db.session.commit()
            return admin
        except Exception as e:
            print("Error creating admin: ", e)
            return None
    
    def __str__(self):
        return self.name
    
    def updated(self):
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        # Delete the dependents associated with the member
        for dependent in self.dependents:
            db.session.delete(dependent)
        
        # Delete the member
        db.session.delete(self)
        
        # Commit the changes
        db.session.commit()

        
        def save(self):
            db.session.add(self)
            db.session.commit()
    
    @property
    def paid_cases(self):
        return [contribution.case_id for contribution in self.contributions if contribution.paid]
    
    def get_contributions(self):
        return [contribution.serialize() for contribution in self.contributions]
    
    def get_dependents(self):
        return [dependent.serialize() for dependent in self.dependents]
    
    def get_cases(self):
        return [case.serialize() for case in self.cases]
    
    def get_not_paid(self):
        return [contribution.serialize() for contribution in self.contributions if not contribution.paid]
    
    @property
    def has_not_contributed_last_3_cases(self):
        last_3_cases = Case.query.order_by(desc(Case.id)).limit(3).all()
        counter = 0

        for case in last_3_cases:
            contribution = Contribution.query.filter_by(member_id=self.id, case_id=case.id).first()
            if contribution and not contribution.paid:
                counter += 1
            else:
                counter += 0
        return (counter)
    
    @property
    def total_contributions_paid(self):
        total_amount = 0.0
        all_contributions = Contribution.query.filter_by(member_id=self.id).all()
        for contribution in all_contributions:
            if contribution.paid:
                total_amount += contribution.case.case_amount
        return total_amount
    
    @property
    def total_cases_not_contributed(self):
        total_cases = Case.query.all()
        counter = 0

        for case in total_cases:
            contribution = Contribution.query.filter_by(member_id=self.id, case_id=case.id).first()
            if contribution and not contribution.paid:
                counter += 1
            else:
                counter += 0
        return (counter)


    def pay_reg_fee(self):
        self.reg_fee_paid = True
        db.session.commit()
