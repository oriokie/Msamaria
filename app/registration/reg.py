# Import necessary modules
from flask import render_template, Blueprint, request, jsonify
from app import db
from app.members.models import Member
from app.dependents.models import Dependent

# Create a Blueprint for the registration routes
regnew_bp = Blueprint('regnew', __name__)

# Route for rendering the registration form
@regnew_bp.route('/regnew', methods=['GET'])
def render_registration_form():
    return render_template('registration_form.html')

# Route for processing member registration and dependent addition
@regnew_bp.route('/regnew', methods=['POST'])
def register_and_add_dependents():
    try:
        # Extract member data from the request form
        member_name = request.form.get('name')
        member_id_number = request.form.get('id_number')
        member_phone_number = request.form.get('phone_number')
        password = member_phone_number

        # Create a new member object
        new_member = Member(name=member_name, id_number=member_id_number, phone_number=member_phone_number, password=password)
        
        # Add the new member to the database
        db.session.add(new_member)
        db.session.commit()

        # Extract dependent data from the request form
        dependents = request.form.getlist('dependent_name')
        phone_numbers = request.form.getlist('dependent_phone_number')
        relationships = request.form.getlist('relationship')

        # Check if dependent data is provided
        if dependents and dependents[0] != '' and dependents[0] != ' ' and dependents[0] != None:
            # Create and add dependents associated with the member
            for name, phone_number, relationship in zip(dependents, phone_numbers, relationships):
                new_dependent = Dependent(name=name, phone_number=phone_number, relationship=relationship, member_id=new_member.id)
                db.session.add(new_dependent)
                db.session.commit()
    
        # Return success message
        return jsonify({'message': 'Member registered and dependents added successfully'}), 200

    except Exception as e:
        # Rollback changes and return error message
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
