"""This is the dependents model"""
from app.db import db
from datetime import datetime


class Dependent(db.Model):
    """This class represents the dependents table."""
    __tablename__ = 'dependents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    is_deceased = db.Column(db.Boolean, default=False)
    relationship = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    

    def __init__(self, name, member_id, phone_number=None, relationship=None):
        self.name = name
        self.phone_number = phone_number
        self.member_id = member_id
        self.relationship = relationship

    def __repr__(self):
        return "<Dependent: {}>".format(self.name)
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'member_id': self.member_id,
            'is_deceased': self.is_deceased,
            'relationship': self.relationship,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def mark_deceased(self):
        self.is_deceased = True
        db.session.commit()

    def isalive(self):
        self.is_deceased = False
        db.session.commit()
    
    def update(self, name, phone_number):
        self.name = name
        self.phone_number = phone_number
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_member(self):
        return self.member_id
