from flask import render_template, redirect, url_for, Blueprint
from app import db
from app.members.models import Member
from app.dependents.models import Dependent
from app.registration.form import RegistrationForm

regnew_bp = Blueprint('regnew', __name__)

@regnew_bp.route('/regnew', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new Member instance and populate its fields
        member = Member(
            name=form.name.data,
            id_number=form.id_number.data,
            phone_number=form.phone_number.data,
            password_hash=form.password.data,  # You should hash the password here
            reg_fee_paid=form.reg_fee_paid.data,
            is_admin=form.is_admin.data,
            is_deceased=form.is_deceased.data
        )
        
        # Add dependents to the member if provided
        for dependent_data in form.dependents.data:
            if dependent_data['name']:
                dependent = Dependent(
                    name=dependent_data['name'],
                    phone_number=dependent_data['phone_number'],
                    relationship=dependent_data['relationship']
                )
                member.dependents.append(dependent)

        # Add the member to the database
        db.session.add(member)
        db.session.commit()
        
        # Redirect to a success page or any other page
        return redirect(url_for('success'))

    return render_template('regnew.html', form=form)


