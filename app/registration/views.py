from flask import render_template, redirect, url_for, flash, Blueprint
from app.members.models import Member
from app.registration.models import RegistrationFee
from app import db
from datetime import datetime

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
