
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.members.models import Member
from app.dependents.models import Dependent
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin.html')

@admin_bp.route('/search_member', methods=['POST'])
@login_required
def search_member():
    if not current_user.is_admin:
        abort(403)
    search_query = request.form.get('search_query', '')
    members = Member.query.filter(
        (Member.name.ilike(f'%{search_query}%')) |
        (Member.alias_name_1.ilike(f'%{search_query}%')) |
        (Member.alias_name_2.ilike(f'%{search_query}%')) |
        (Member.phone_number.ilike(f'%{search_query}%'))
    ).all()
    return jsonify([member.serialize(include_dependents=True) for member in members])

@admin_bp.route('/member_details/<int:member_id>', methods=['GET'])
@login_required
def get_member_details(member_id):
    if not current_user.is_admin:
        abort(403)
    member = Member.query.get_or_404(member_id)
    return jsonify(member.serialize(include_dependents=True))

def get_dependent_by_id(dependent_id):
    return Dependent.query.filter_by(id=dependent_id).first()

@admin_bp.route('/update_member/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    member = Member.query.get(member_id)

    if not member:
        return jsonify({"error": "Member not found"}), 404

    # Update member fields
    member.name = data.get('name')
    member.id_number = data.get('id_number')
    member.phone_number = data.get('phone_number')
    member.alias_name_1 = data.get('alias_name_1')
    member.alias_name_2 = data.get('alias_name_2')
    member.reg_fee_paid = data.get('reg_fee_paid', False)
    member.is_admin = data.get('is_admin', False)
    member.active = data.get('active', True)
    member.is_deceased = data.get('is_deceased', False)
    
    # Handle dependents
    existing_dependent_ids = [d['id'] for d in data.get('dependents', []) if d.get('id')]
    current_dependents = {dependent.id: dependent for dependent in member.dependents}
    
    # Update existing dependents or delete those that are not in the list
    for dependent_id, dependent in current_dependents.items():
        if dependent_id not in existing_dependent_ids:
            dependent.delete()  # Delete dependents that are not in the updated list
        else:
            for d in data['dependents']:
                dependent = get_dependent_by_id(d['id'])  # Assuming you have a function to get the dependent by id
                if dependent:
                    dependent.update(
                        name=d.get('name'),  # Using .get() ensures it won't raise KeyError if the field is missing
                        phone_number=d.get('phone_number')  # You can set a default value if necessary
        )


    # Add new dependents
    for dependent_data in data.get('dependents', []):
        if not dependent_data.get('id'):  # New dependent
            new_dependent = Dependent(
                name=dependent_data['name'],
                member_id=member.id,
                relationship=dependent_data.get('relationship'),
                phone_number=dependent_data.get('phone_number')
            )
            db.session.add(new_dependent)

    try:
        db.session.commit()
        return jsonify({"message": "Member updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/delete_dependent/<int:dependent_id>', methods=['DELETE'])
@login_required
def delete_dependent(dependent_id):
    try:
        dependent = Dependent.query.get(dependent_id)
        if not dependent:
            return jsonify({"error": "Dependent not found"}), 404
        
        db.session.delete(dependent)
        db.session.commit()
        return jsonify({"success": True, "message": "Dependent deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/register_member', methods=['POST'])
@login_required
def register_member():
    if not current_user.is_admin:
        abort(403)
    data = request.json
    new_member = Member(
        name=data['name'],
        id_number=data['id_number'],
        phone_number=data['phone_number'],
        alias_name_1=data.get('alias_name_1'),
        alias_name_2=data.get('alias_name_2'),
        reg_fee_paid=data.get('reg_fee_paid', False),
        is_admin=data.get('is_admin', False),
        active=data.get('active', True),
        is_deceased=data.get('is_deceased', False)
    )
    new_member.set_password(data['password'])
    
    try:
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'New member registered successfully', 'member_id': new_member.id})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Registration failed. The ID number may already be in use.'}), 400

@admin_bp.route('/delete_member/<int:member_id>', methods=['DELETE'])
@login_required
def delete_member(member_id):
    if not current_user.is_admin:
        abort(403)
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})
