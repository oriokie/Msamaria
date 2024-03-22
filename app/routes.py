from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from app.members.models import Member
from .db import db
from app import login_manager
from flask import session
from app.cases.models import Case
from sqlalchemy import desc
from app.contributions.models import Contribution


# Create a Blueprint instance
bp = Blueprint('routes', __name__)

# Create a Blueprint instance for admin routes
#admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Define route handlers
@bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('routes.profile'))
    else:
        return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        id_number = request.form['id_number']
        phone_number = request.form['phone_number']
        passwd = request.form['password']

        # Check if the ID number already exists
        existing_member = Member.query.filter_by(id_number=id_number).first()
        if existing_member:
            flash('ID number already exists. Please choose a different one.', 'error')
            return redirect(url_for('routes.register'))

        # Create a new member
        new_member = Member(name=name, id_number=id_number, phone_number=phone_number, password=passwd)

        # Add the new member to the database
        db.session.add(new_member)
        db.session.commit()

        # Log in the newly registered user
        login_user(new_member)

        flash('Registration successful. Proceed to Pay KES.500 to 0700000000 and forward the Message', 'success')
        return redirect(url_for('routes.profile', user=new_member))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("Debug: Login route accessed")
    if current_user.is_authenticated:
        return redirect(url_for('routes.profile'))  # Redirect to profile if user is already logged in
    
    if request.method == 'POST':
        id_number = request.form['id_number']
        password = request.form['password']
        print(f"Debug: Received login data - ID Number: {id_number}, Password: {password}")

        # Find the member by ID number
        member = Member.query.filter_by(id_number=id_number).first()

        if member and member.check_password(password):
            login_user(member)  # Log in the user
            flash('Login successful.', 'success')
            print("Debug: Authentication successful")
            user = current_user
            return redirect(url_for('routes.profile', user=user))  # Redirect to the profile page
        else:
            print("Debug: Authentication failed")
            flash('Invalid ID number or password.', 'error')

    return render_template('login.html')

@bp.route('/profile')
@login_required
def profile():
    print("Debug: Profile route accessed")
    # Fetch the current user's details
    user = current_user
    is_admin = user.is_admin
    # is_active = user.active or user.active is not None

    print(f"Debug: User details - Name: {user.name}, ID Number: {user.id_number}, Phone Number: {user.phone_number}, Admin: {is_admin}")
     # Check if the user is an admin

    if is_admin:
        # Fetch all users if the current user is an admin
        users = Member.query.filter_by(active=True).all()
    else:
        users = []  # Set users to None for non-admin users
        
    last_3_cases = Case.query.order_by(desc(Case.id)).limit(3).all()
    print(f"Debug: Last 3 cases - {last_3_cases}")

    if user.is_authenticated and is_admin:
        defaulters = [member for member in users if member.has_not_contributed_last_3_cases == 3]
    else:
        defaulters = []

    Defaulted_cases = user.has_not_contributed_last_3_cases
    total_case_contributions = user.total_contributions_paid
    no_of_defaulted_cases = user.total_cases_not_contributed

    return render_template('profile.html',
                           user=user, is_admin=is_admin, users=users,
                           defaulters=defaulters,
                           Defaulted_cases=Defaulted_cases,
                           last_3_cases=last_3_cases,
                           total_case_contributions=total_case_contributions,
                           no_of_defaulted_cases=no_of_defaulted_cases)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))


# # Route for the admin page
# @admin_bp.route('/')
# @login_required
# def admin():
#     # Check if the current user is an admin
#     if not current_user.is_admin:
#         flash('You do not have permission to access the admin page.', 'error')
#         return redirect(url_for('routes.home'))

#     # Fetch all users from the database
#     users = Member.query.all()

#     # Render the admin template with user data
#     return render_template('admin.html', users=users)

# # Route for editing user information
# @admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def edit_user(user_id):
#     # Check if the current user is an admin
#     if not current_user.is_admin:
#         flash('You do not have permission to edit users.', 'error')
#         return redirect(url_for('routes.home'))

#     # Fetch the user to be edited from the database
#     user = Member.query.get(user_id)

#     if request.method == 'POST':
#         # Update user information based on the form data
#         user.name = request.form['name']
#         user.id_number = request.form['id_number']
#         user.phone_number = request.form['phone_number']
#         user.is_admin = bool(request.form.get('is_admin'))  # Update admin status

#         # Commit changes to the database
#         db.session.commit()

#         flash('User information updated successfully.', 'success')
#         return redirect(url_for('admin.admin'))

#     # Render the edit user template with user data
#     return render_template('edit_user.html', user=user)

# # Route for deactivating a user account
@bp.route('/deactivate-user/<int:user_id>', methods=['POST'])
@login_required
def deactivate_user(user_id):
    if request.method == 'POST':
        # Fetch the user to be deactivated from the database
        user = Member.query.get(user_id)

        # Deactivate the user
        user.deactivate()

        # Commit changes to the database
        db.session.commit()
    else:
        abort(405)

    flash('User account deactivated successfully.', 'success')
    return redirect(url_for('routes.profile'))

