from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from app import db
from app.finance.models import Expense
from app.cases.models import Case


expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/expenses', methods=['GET'])
def expenses():
    
    # Fetch the last 5 expenses
    expenses = Expense.query.order_by(Expense.created_at.desc()).limit(2).all()

    # Fetch active cases
    cases = Case.query.filter_by(closed=False).all()


    return render_template('expenses.html', expenses=expenses, cases=cases)

@expense_bp.route('/get_expenses_by_case', methods=['POST'])
def get_expenses_by_case():
    case_id = request.form.get('case_id')
    expenses = Expense.query.filter_by(case_id=case_id).order_by(Expense.created_at.desc()).all()

    # Render a template fragment containing expenses table rows
    return render_template('expenses_table_rows.html', expenses=expenses)

@expense_bp.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        db.session.commit()
        return redirect(url_for('expenses.expenses'))
    return render_template('edit_expense.html', expense=expense)


@expense_bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('expenses.expenses'))

@expense_bp.route('/add_expense_page', methods=['GET'])
def add_expense_page():
    case_id = request.args.get('case_id')
    if not case_id:
        # Handle case ID not provided
        pass
    return render_template('add_expense.html', case_id=case_id)

@expense_bp.route('/add_expense', methods=['POST'])
def add_expense():
    case_id = request.form['case_id']
    description = request.form['description']
    amount = float(request.form['amount'])
    
    expense = Expense(case_id=case_id, description=description, amount=amount)
    db.session.add(expense)
    db.session.commit()
    
    return redirect(url_for('expenses.expenses'))


@expense_bp.route('/update_expense', methods=['POST'])
def update_expense():
    try:
        expense_id = request.form.get('expense_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        
        # Retrieve the expense from the database
        expense = Expense.query.get_or_404(expense_id)
        
        # Update the expense with the new values
        expense.description = description
        expense.amount = amount
        
        # Commit the changes to the database
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

