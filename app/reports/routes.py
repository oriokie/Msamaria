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


import plotly.graph_objs as go
from flask import current_app

@reports_bp.route('/total_collections_chart')
def total_collections_chart():
    # Query database to get information about the 10 most recent cases
    cases = Case.query.order_by(Case.id.desc()).limit(10).all()

    # Extract data for the chart
    case_ids = []
    total_amount_contributed = []

    for case in cases:
        case_ids.append(case.id)
        # Calculate summary information for each case
        active_members_contributed = len(set(contribution.member_id for contribution in case.contributions if contribution.paid))
        total_amount = active_members_contributed * case.case_amount

        # Calculate total amount contributed for each case
        total_amount_contributed.append(total_amount)

    current_app.logger.info("Case IDs: %s", case_ids)
    current_app.logger.info("Total Amounts: %s", total_amount_contributed)

    # Create a bar chartx
    bar_chart = go.Bar(
        x=case_ids,
        y=total_amount_contributed,
        marker=dict(color='blue')  # Set color of bars
    )

    # Create layout for the chart
    layout = go.Layout(
        title='Total Collections for Current 10 Cases',
        xaxis=dict(title='Case ID'),
        yaxis=dict(title='Total Amount Contributed')
    )

    # Create figure
    fig = go.Figure(data=[bar_chart], layout=layout)

    # Convert figure to JSON for embedding in HTML
    chart_json = fig.to_json()

    # Calculate the counts of active members who have contributed and not contributed to the most recent case
    recent_case = Case.query.order_by(Case.id.desc()).first()
    active_members_contributed = len(set(contribution.member_id for contribution in recent_case.contributions if contribution.paid))
    active_members_not_contributed = len(set(contribution.member_id for contribution in recent_case.contributions if not contribution.paid))

    # Create labels and values for the pie chart
    pie_labels = ['Contributed', 'Not Contributed']
    pie_values = [active_members_contributed, active_members_not_contributed]

    # Create a pie chart
    pie_chart = go.Pie(
        labels=pie_labels,
        values=pie_values,
        hole=0.3  # Set the size of the center hole
    )

    # Create layout for the pie chart
    pie_layout = go.Layout(
        title='Contribution Status for Most Recent Case',
    )

    # Create figure for the pie chart
    pie_fig = go.Figure(data=[pie_chart], layout=pie_layout)

    # Convert pie chart figure to JSON for embedding in HTML
    pie_chart_json = pie_fig.to_json()


    return render_template('total_collections_chart.html', chart_json=chart_json, pie_chart_json=pie_chart_json)