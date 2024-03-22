# Import necessary modules
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from .models import Case
from app.cases.utils import fetch_member_id, get_member_name, get_dependent_name
from flask_login import login_required


# Define a Blueprint for the active cases route
active_cases_bp = Blueprint('active_cases', __name__, url_prefix='/active-cases')

# Route for viewing active cases
@active_cases_bp.route('/')
@login_required
def view_active_cases():
    # Query active cases from the database
    active_cases = Case.query.filter_by(closed=False).all()

    # Create a list to store case details along with deceased person names
    active_cases_data = []
    for case in active_cases:
        case_id = case.id
        if case.dependent_id:
            deceased_member = get_dependent_name(case.dependent_id)
        else:
            deceased_member = get_member_name(case.member_id)
        active_cases_data.append((case, case_id, deceased_member))

    return render_template('active_cases.html', active_cases=active_cases_data)

# Route for closing an open case
@active_cases_bp.route('/close/<int:case_id>', methods=['POST'])
@login_required
def close_case(case_id):
    # Query the case by its ID
    case = Case.query.get_or_404(case_id)

    # Close the case
    case.close_case()
    db.session.commit()

    return redirect(url_for('active_cases.view_active_cases'))


# Define the route for editing cases
@active_cases_bp.route('/edit-case/<int:case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    # Retrieve the case from the database
    case = Case.query.get_or_404(case_id)

    if request.method == 'POST':
        # Update the case details based on the form submission
        case_amount = float(request.form.get('case_amount'))
        case.case_amount = case_amount
        
        # Commit the changes to the database
        db.session.commit()
        
        # Flash a success message
        flash('Case details updated successfully.', 'success')
        
        # Redirect the user to the active cases page or any other appropriate page
        return redirect(url_for('active_cases.view_active_cases'))
    
    # If it's a GET request, render the edit case form with the case details
    return render_template('edit_case.html', case=case)