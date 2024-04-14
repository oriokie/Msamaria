from flask import send_file, Blueprint, render_template
import csv
from flask import make_response
import io
from app.members.models import Member
from app.cases.models import Case
from app.members.models import Dependent
from app.cases.utils import fetch_member_id, get_member_name, get_dependent_name

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

@reports_bp.route('/case_summary')
def case_summary():
    # Query database to get information about all cases
    cases = Case.query.all()

    # Initialize a list to store case summaries
    case_summaries = []

    total_amount_contributed_sum = 0
    active_members_contributed_sum = 0
    active_members_not_contributed_sum = 0
    total_expenses_sum = 0
    total_amount_sum = 0

    for case in cases:
        if case.dependent_id:
            deceased_member = get_dependent_name(case.dependent_id)
        else:
            deceased_member = get_member_name(case.member_id)

        # Calculate total expenses for the case
        total_expenses = sum(expense.amount for expense in case.expenses)

        # Calculate summary information for each case
        active_members_contributed = len(set(contribution.member_id for contribution in case.contributions if contribution.paid))
        active_members_not_contributed = len(set(contribution.member_id for contribution in case.contributions if not contribution.paid))
        total_amount_contributed = active_members_contributed * case.case_amount
        total_amount = total_amount_contributed - total_expenses

        # Update the sum of each column
        total_amount_contributed_sum += total_amount_contributed
        active_members_contributed_sum += active_members_contributed
        active_members_not_contributed_sum += active_members_not_contributed
        total_expenses_sum += total_expenses
        total_amount_sum += total_amount

        # Create a dictionary to store case summary information
        case_summary = {
            'id': case.id,
            'deceased_person': deceased_member,
            'total_amount_contributed': total_amount_contributed,
            'active_members_contributed': active_members_contributed,
            'active_members_not_contributed': active_members_not_contributed,
            'total_expenses': total_expenses,
            'total_amount': total_amount,
        }

        # Append the case summary to the list
        case_summaries.append(case_summary)

    # Add a row for the summation of totals
    total_row = {
        'id': 'Total',
        'deceased_person': '',
        'total_amount_contributed': total_amount_contributed_sum,
        'active_members_contributed': active_members_contributed_sum,
        'active_members_not_contributed': active_members_not_contributed_sum,
        'total_expenses': total_expenses_sum,
        'total_amount': total_amount_sum,
    }
    case_summaries.append(total_row)

    return generate_csv_response(case_summaries, 'case_summary_report.csv')

