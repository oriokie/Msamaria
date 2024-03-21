from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from .models import Case
from app.members.models import Member
from app.dependents.models import Dependent
from datetime import datetime
from flask_login import login_required
from flask import current_app as app
from flask import jsonify
from app.cases.utils import fetch_member_id
from app.contributions.models import Contribution

cases_bp = Blueprint('cases', __name__, url_prefix='/cases')

# Route for searching members and dependents
@cases_bp.route('/', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        members = Member.query.filter(Member.name.ilike(f'%{search_query}%')).limit(3).all()
        dependents = Dependent.query.filter(Dependent.name.ilike(f'%{search_query}%')).limit(3).all()
        return render_template('cases.html', members=members, dependents=dependents)
    return render_template('cases.html')

## Route for creating a new case
@cases_bp.route('/create', methods=['POST'])
@login_required
def create_case():
    try:
        member_id = request.form.get('member_id')
        dependent_id = request.form.get('dependent_id')
        case_amount = float(request.form.get('case_amount')) if request.form.get('case_amount') else 0.0

        print(f"Debug: Member ID: {member_id}, Dependent ID: {dependent_id}, Case Amount: {case_amount}")

       # If dependent_id is None or not provided, create the case without specifying a dependent
        if dependent_id == 'None' or dependent_id == 'null' or not dependent_id:
            dependent_id = None

        # If the member_deceased option is checked, mark the member as deceased
        if member_id and dependent_id is None:
            member = Member.query.get(member_id)
            if member:
                member.mark_deceased()

        if dependent_id:
            dependent = Dependent.query.get(dependent_id)
            if dependent:
                # Mark dependent as deceased
                dependent.mark_deceased()

        # Create the case
        case = Case(member_id=member_id, dependent_id=dependent_id, case_amount=case_amount)
        db.session.add(case)
        db.session.commit()
        flash('Case created successfully.', 'success')

        # Generate contribution records for all active members
        generate_contributions_for_case(case)

        return redirect(url_for('cases.search'))
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the case. Please try again.', 'error')
        app.logger.error(f'Error creating case: {str(e)}')
        return redirect(url_for('cases.search'))

@cases_bp.route('/get-member-id', methods=['POST'])
@login_required
def get_member_id():
    dependent_id = request.form.get('dependent_id')
    # Logic to fetch the member ID based on the dependent ID
    # Example: member_id = fetch_member_id(dependent_id)
    member_id = fetch_member_id(dependent_id)  # Replace this with your logic
    print(f"Member ID: {member_id}")
    return jsonify({'member_id': member_id})

# Function to generate contribution records for all active members when a new case is created
def generate_contributions_for_case(case):
    active_members = Member.query.filter_by(active=True).all()
    for member in active_members:
        contribution = Contribution(
            member_id=member.id,
            case_id=case.id,
            paid=False  # Set paid column as False initially
        )
        db.session.add(contribution)
    db.session.commit()