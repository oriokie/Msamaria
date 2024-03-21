#This is the members model

from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.orm import relationship  # Import relationship from SQLAlchemy



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
            'is_active': self.active,
            'is_deceased': self.is_deceased,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }

        # Optionally include dependents
        if include_dependents:
            serialized_member['dependents'] = [dependent.serialize() for dependent in self.dependents]

        return serialized_member


    def activate(self):
        self.is_active = True
        db.session.commit()
    
    def deactivate(self):
        self.is_active = False
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
        admin = Member(name="Admin", id_number="8888888888", phone_number="0700000000", password="admin")
        admin.make_admin()
        admin.activate()
        admin.is_authenticated = True
        db.session.add(admin)
        db.session.commit()
        return admin
    
    def __str__(self):
        return self.name
    
    def updated(self):
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @property
    def paid_cases(self):
        return [contribution.case_id for contribution in self.contributions if contribution.paid]
    
    
