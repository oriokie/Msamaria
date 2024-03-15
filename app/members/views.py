from flask import Blueprint, request, jsonify
from app.db import db
from app.members.models import Member

members_bp = Blueprint('members', __name__)

@members_bp.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.serialize() for member in members])

@members_bp.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify(member.serialize())

@members_bp.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    name = data.get('name')
    id_number = data.get('id_number')
    phone_number = data.get('phone_number')
    password = data.get('password')

    if not all([name, id_number, phone_number, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_member = Member.query.filter_by(id_number=id_number).first()
    if existing_member:
        return jsonify({'error': 'Member with the same ID number already exists'}), 409

    new_member = Member(name=name, id_number=id_number, phone_number=phone_number, password=password)
    db.session.add(new_member)
    db.session.commit()
    return jsonify(new_member.serialize()), 201

@members_bp.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    name = data.get('name')
    id_number = data.get('id_number')
    phone_number = data.get('phone_number')
    password = data.get('password')

    if name:
        member.name = name
    if id_number:
        member.id_number = id_number
    if phone_number:
        member.phone_number = phone_number
    if password:
        member.set_password(password)

    db.session.commit()
    return jsonify(member.serialize())

@members_bp.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return '', 204
