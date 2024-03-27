from flask import render_template, request, redirect, url_for, Blueprint
from app import db
from app.finance.models import Expense
from app.cases.models import Case


expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/expenses', methods=['GET'])
def expenses():
    
    # Fetch the last 5 expenses
    expenses = Expense.query.order_by(Expense.created_at.desc()).limit(2).all()

    # Fetch active cases
    active_cases = Case.query.filter_by(closed=False).all()


    return render_template('expenses.html', expenses=expenses, active_cases=active_cases)

@expense_bp.route('/add_expense', methods=['POST'])
def add_expense():
    case_id = request.form['case_id']
    description = request.form['description']
    amount = float(request.form['amount'])
    
    expense = Expense(case_id=case_id, description=description, amount=amount)
    expense.save()
    
    return redirect(url_for('expenses.expenses'))

@expense_bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.get_expense_by_id(expense_id)
    if expense:
        expense.delete()
    
    return redirect(url_for('expenses.expenses'))
