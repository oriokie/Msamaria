"""Module for the routes for the dependents"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from app.db import db
from app.members.models import Member
from app.dependents.models import Dependent
from app import login_manager
from flask_login import login_user, current_user, logout_user, login_required


dependents_bp = Blueprint('dependents', __name__, url_prefix='/dependents')


@dependents_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_dependent():
    data = request.get_json()
    name = data.get('name')
    phone_number = data.get('phone_number')
    relationship = data.get('relationship')
    member_id = current_user.id

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    dependent = Dependent(name=name, phone_number=phone_number, member_id=member_id, relationship=relationship)
    db.session.add(dependent)
    db.session.commit()

    flash('Dependent added successfully', 'success')  # Flash success message

    dependents = Dependent.query.filter_by(member_id=member_id).all()  # Get all dependents for the current user
    dependents_data = [dependent.serialize() for dependent in dependents]  # Serialize dependents data
    return jsonify(dependents_data), 201


@dependents_bp.route('/', methods=['GET'])
@login_required
def get_dependents():
    try:
        dependents = Dependent.query.filter_by(member_id=current_user.id).all()
        dependents_data = [dependent.serialize() for dependent in dependents]
        return jsonify(dependents_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500