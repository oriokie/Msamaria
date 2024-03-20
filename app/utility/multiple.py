from flask import Blueprint, request, jsonify
from app import db
from app.members.models import Member
from app.dependents.models import Dependent
import csv
import io
import logging

csv_bp = Blueprint('csv', __name__, url_prefix='/csv')
logger = logging.getLogger(__name__)

@csv_bp.route('/upload', methods=['POST'])
def upload_csv():
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        members = []
        dependents = []

        # Parse CSV file
        csv_data = csv.DictReader(io.StringIO(file.stream.read().decode("latin-1")))
        for row in csv_data:
            # Check if member with the same phone number already exists
            existing_member = Member.query.filter_by(phone_number=row['member_phone_number']).first()
            if existing_member:
                logger.info(f'Skipping creation of member with phone number {row["member_phone_number"]} as it already exists')
                member = existing_member
            else:
                # Create member
                member = Member(
                    name=row['member_name'],
                    id_number=row['member_id_number'],
                    phone_number=row['member_phone_number'],
                    password=row['member_phone_number']  # Using phone number as password
                )
                db.session.add(member)
                logger.info(f'Member created: {member}')
                members.append(member)
                # Commit the member to the database to generate the member id
                db.session.commit()

            # Iterate over each column in the row
            for column, value in row.items():
                # If the column is empty or not related to dependents, skip it
                if not value or column.startswith('member_'):
                    continue
                
                # Create dependent with relationship based on column name
                relationship = get_relationship(column)
                dependent = Dependent(
                    name=value,
                    member_id=member.id,
                    relationship=relationship
                )
                db.session.add(dependent)
                logger.info(f'Dependent created: {dependent}')
                dependents.append(dependent)

        # Commit all changes to the database
        db.session.commit()

        return jsonify({'message': 'Members and dependents created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error during CSV upload: {str(e)}')
        return jsonify({'error': str(e)}), 500

def get_relationship(column):
    # Map column names to relationships
    relationships = {
        'Spouse': 'Spouse',
        'Contributor\'s Father': 'Father',
        'Contributor\'s Mother': 'Mother',
        'Spouse\'s Father': 'Father',
        'Spouse\'s Mother': 'Mother',
        'First Child': 'Child',
        'Second Child': 'Child',
        'Third Child': 'Child',
        'Fourth Child': 'Child',
        'Fifth Child': 'Child'
    }
    return relationships.get(column, 'Unknown')
