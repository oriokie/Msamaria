from app import db
from datetime import datetime
from app.cases.models import Case

class Expense(db.Model):
    """This class represents the expenses table."""
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at =  db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)


    def __repr__(self):
        return "<Expense: {}>".format(self.description)
    
    def serialize(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'description': self.description,
            'amount': self.amount,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_expense_by_id(expense_id):
        """Retrieve an expense by its ID."""
        return Expense.query.get(expense_id)

    def get_all_expenses():
        """Retrieve all expenses."""
        return Expense.query.all()

    def get_expenses_by_case(case_id):
        """Retrieve all expenses for a given case."""
        return Expense.query.filter_by(case_id=case_id).all()

    def get_total_expenses(case_id):
        """Retrieve the total amount of expenses for a given case."""
        expenses = Expense.query.filter_by(case_id=case_id).all()
        total = 0
        for expense in expenses:
            total += expense.amount
        return total
    
    def update(self, description, amount):
        self.description = description
        self.amount = amount
        db.session.commit()
