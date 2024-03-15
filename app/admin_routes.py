from flask import Blueprint, render_template, request, jsonify, flash
from app.members.models import Member
from app.dependents.models import Dependent
from app import db
from flask_login import current_user
from flask_login import login_required


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
def admin_dashboard():
    if current_user.is_authenticated and current_user.is_admin:
        return render_template('admin.html')
    else:
        return render_template('403.html'), 403

# Route for searching members by name
@admin_bp.route('/search_member', methods=['POST'])
@login_required
def search_member():
    search_query = request.form.get('search_query')
    # Perform a search query to find the member by name
    members = Member.query.filter(Member.name.ilike(f'%{search_query}%')).all()
    if members:
        # Serialize the list of members
        serialized_members = [member.serialize(include_dependents=True) for member in members]
        return jsonify(serialized_members)
    else:
        return jsonify([])  # Return an empty list if no members are found

# Route for getting member details by ID
@admin_bp.route('/member_details/<int:member_id>', methods=['GET'])
@login_required
def get_member_details(member_id):
    # Retrieve member by ID
    member = Member.query.get(member_id)
    if member:
        # Serialize member details
        serialized_member = member.serialize(include_dependents=True)
        return jsonify(serialized_member)
    else:
        return jsonify({'error': 'Member not found'}), 404
# Update Member Route
@admin_bp.route('/update_member/<int:member_id>', methods=['POST'])
@login_required
def update_member(member_id):
    member = Member.query.get(member_id)
    if member:
        # Extract updated data from the request
        data = request.json
        # Update member fields
        member.name = data.get('name')
        member.id_number = data.get('id_number')
        member.phone_number = data.get('phone_number')
        member.reg_fee_paid = data.get('reg_fee_paid')
        member.is_admin = data.get('is_admin')
        member.active = data.get('is_active')
        member.is_deceased = data.get('is_deceased')
        # Update dependents (if applicable)
        for dependent_data in data.get('dependents', []):
            dependent_id = dependent_data.get('id')
            dependent = Dependent.query.get(dependent_id)
            if dependent:
                dependent.name = dependent_data.get('name')
        db.session.commit()
        return jsonify({'message': 'Member details updated successfully'})
    else:
        return jsonify({'error': 'Member not found'}), 404

# Route for deleting a dependent
@admin_bp.route('/delete_dependent/<int:dependent_id>', methods=['DELETE'])
@login_required
def delete_dependent(dependent_id):
    # Retrieve dependent by ID
    dependent = Dependent.query.get(dependent_id)
    if dependent:
        # Delete dependent from the database
        db.session.delete(dependent)
        # Commit changes to the database
        db.session.commit()
        flash('Dependent deleted successfully', 'success')
        return jsonify({'success': 'Dependent deleted successfully'})
    else:
        flash('Dependent not found', 'error')
        return jsonify({'error': 'Dependent not found'}), 404