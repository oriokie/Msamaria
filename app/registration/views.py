from flask import render_template, redirect, url_for, flash, Blueprint, request
from app.members.models import Member
from app.registration.models import RegistrationFee
from app import db
from datetime import datetime
from sqlalchemy import extract, func
from calendar import month_name
from .models import RegistrationFee

reg_bp = Blueprint('registration', __name__)


@reg_bp.route('/register_fee/<int:member_id>', methods=['POST'])
def register_fee(member_id):
    # Retrieve the member by ID
    member = Member.query.get(member_id)
    if member:
        # Update reg_fee_paid to True
        member.reg_fee_paid = True
        # Create a new RegistrationFee record
        reg_fee = RegistrationFee(member_id=member.id, amount=500, date_paid=datetime.now())
        db.session.add(reg_fee)
        db.session.commit()
        flash('Registration fee successfully paid.', 'success')
    else:
        flash('Member not found.', 'error')
    return redirect(url_for('routes.profile', user_id=member_id))

@reg_bp.route('/decline_registration/<int:member_id>', methods=['POST'])
def decline_registration(member_id):
    # Retrieve the member by ID
    member = Member.query.get(member_id)
    if member:
        Member.delete(member)
        flash('Registration declined.', 'success')
    else:
        flash('Member not found.', 'error')
    return redirect(url_for('routes.profile', user_id=member_id))

@reg_bp.route('/registration-fees', methods=['GET'])
def get_monthly_registration_fees():
    # Get the year from query parameters, default to current year
    current_year = datetime.now().year
    selected_year = request.args.get('year', default=current_year, type=int)

    # Query to get monthly totals
    monthly_fees = db.session.query(
        extract('month', RegistrationFee.date_paid).label('month'),
        func.sum(RegistrationFee.amount).label('total')
    ).filter(
        extract('year', RegistrationFee.date_paid) == selected_year
    ).group_by(
        extract('month', RegistrationFee.date_paid)
    ).order_by(
        extract('month', RegistrationFee.date_paid)
    ).all()

    # Create a dictionary with all months initialized to 0
    result = {month: 0 for month in range(1, 13)}

    # Update the result with actual data
    for month, total in monthly_fees:
        result[month] = float(total)

    # Create a dictionary of month names
    month_names = {i: month_name[i] for i in range(1, 13)}

    return render_template('registration_fees.html', 
                           monthly_fees=result, 
                           current_year=current_year, 
                           selected_year=selected_year,
                           month_names=month_names)
