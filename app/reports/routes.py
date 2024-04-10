from flask import send_file, Blueprint, render_template
import csv
from flask import make_response
import io
from app.members.models import Member
from app.cases.models import Case
from app.members.models import Dependent


reports_bp = Blueprint('reports', __name__)

# Route for displaying the page with download buttons
@reports_bp.route('/reports')
def reports():
    return render_template('reports.html')

@reports_bp.route('/generate_active_members_report')
def generate_active_members_report():
    active_members = Member.query.filter_by(active=True,
                                            is_deceased=False,
                                            reg_fee_paid=True).all()
    report_data = []

    for member in active_members:
        # Get dependents for the current member
        dependents = Dependent.query.filter_by(member_id=member.id).all()

        # Create a list to store dependent information
        dependent_info = []
        for dependent in dependents:
            dependent_info.append({
                'Name': dependent.name,
                'Relationship': dependent.relationship,
                # Add more fields as needed
            })

        # Append member and dependent information to the report data
        report_data.append({
            'Member ID': member.id,
            'Member Name': member.name,
            'Member ID Number': member.id_number,
            'Member Phone Number': member.phone_number,
            'Dependents': dependent_info
        })

    return generate_csv_response(report_data, 'active_members_report.csv')


@reports_bp.route('/generate_inactive_members_report')
def generate_inactive_members_report():
    inactive_members = Member.query.filter_by(active=False).all()
    report_data = []
    for member in inactive_members:
        report_data.append({
            'ID': member.id,
            'Name': member.name,
            'ID Number': member.id_number,
            'Phone Number': member.phone_number
            # Add more fields as needed
        })

    return generate_csv_response(report_data, 'inactive_members_report.csv')

@reports_bp.route('/generate_case_summary_report')
def generate_case_summary_report():
    cases = Case.query.all()
    report_data = []
    for case in cases:
        report_data.append({
            'ID': case.id,
            'Deceased Person': case.deceased_member.name if case.deceased_member else 'N/A',
            'Total Amount Contributed': case.total_amount_contributed,
            'Active Members Contributed': case.active_members_contributed,
            'Active Members Not Contributed': case.active_members_not_contributed,
            # Add more fields as needed
        })

    return generate_csv_response(report_data, 'case_summary_report.csv')

def generate_csv_response(data, filename):
    output = make_response(generate_csv(data))
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output

def generate_csv(data):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()
