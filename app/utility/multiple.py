from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from app import db
from app.members.models import Member
from app.dependents.models import Dependent
import csv
import io
import logging
from app.contributions.models import Contribution
from app.cases.models import Case

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
        csv_data = csv.DictReader(io.StringIO(file.stream.read().decode("utf-8")))
        for row in csv_data:
            # Remove BOM from the 'name' field if present
            if '\ufeffname' in row:
                row['name'] = row.pop('\ufeffname')
            # Ensure all expected fields are present
            required_fields = ['name', 'phone_number']
            for field in required_fields:
                if field not in row or not row[field].strip():
                    logger.error(f"Missing or empty field '{field}' in row: {row}")
                    continue  # Skip this row if required fields are missing
            # Check if member with the same phone number already exists
            existing_member = Member.query.filter_by(phone_number=row['phone_number']).first()
            if existing_member:
                logger.info(f'Skipping creation of member with phone number {row["phone_number"]} as it already exists')
                member = existing_member
            else:
                # Create member
                member = Member(
                    name=row['name'],
                    alias_name_1=row['alias_name_1'],
                    alias_name_2=row['alias_name_2'],
                    id_number=row['id_number'],
                    phone_number=row['phone_number'],
                    password=row['phone_number'],  # Using phone number as password
                    reg_fee_paid=bool(int(row['reg_fee_paid'])),
                    is_admin=bool(int(row['is_admin'])),
                    active=bool(int(row['active'])),
                    is_deceased=bool(int(row['is_deceased']))
                )
                db.session.add(member)
                logger.info(f'Member created: {member}')
                members.append(member)
                # Commit the member to the database to generate the member id
                db.session.commit()

            # Iterate over each column in the row
            dependent_columns = ['spouse', 'contributor_father', 'contributor_mother', 'spouse_father', 'spouse_mother', 
                                 'first_child', 'second_child', 'third_child', 'fourth_child', 'fifth_child']
            for column in dependent_columns:
                value = row.get(column)
                if value:
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
        'spouse': 'Spouse',
        'contributor_father': 'Father',
        'contributor_mother': 'Mother',
        'spouse_father': 'Father-in-law',
        'spouse_mother': 'Mother-in-law',
        'first_child': 'Child',
        'second_child': 'Child',
        'third_child': 'Child',
        'fourth_child': 'Child',
        'fifth_child': 'Child'
    }
    return relationships.get(column, 'Unknown')


@csv_bp.route('/upload_pay', methods=['GET', 'POST'])
def upload_contributions():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Assuming the CSV file has headers 'case_id' and 'member_id'
            for line in file.readlines():
                try:
                    line = line.decode('utf-8')  # Decode bytes-like object to string
                    case_id, member_id = line.strip().split(',')
                    # Check if case_id and member_id exist in the database
                    case = Case.query.get(case_id)
                    member = Member.query.get(member_id)
                    if case and member:
                        # Create contribution
                        #print(f'Creating contribution for member {member_id} and case {case_id}')
                        contribution = Contribution.bulk_mark_as_paid(int(member_id), int(case_id))  # Pass both arguments
                        print(f"bulk_mark_as_paid received member_id: {member_id}, case_id: {case_id}")  # Debugging print

                except ValueError:
                    flash(f'Invalid data format on line: {line.strip()}')
                    continue  # Skip this line and move to the next
                except Exception as e:
                    flash(f'Error processing line: {line.strip()}. Error: {str(e)}')
                    continue  # Skip this line and move to the next
            flash('Contributions uploaded successfully')
            return redirect(url_for('routes.profile'))  # Redirect back to upload page
    return render_template('profile.html')

@csv_bp.route('/download', methods=['GET'])
def download_csv():
    members = Member.query.all()
    dependents = Dependent.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['member_name', 'member_id_number', 'member_phone_number', 'dependent_name', 'relationship'])
    for member in members:
        writer.writerow([member.name, member.id_number, member.phone_number, '', ''])
        for dependent in dependents:
            if dependent.member_id == member.id:
                writer.writerow(['', '', '', dependent.name, dependent.relationship])
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=members_and_dependents.csv'
    }

