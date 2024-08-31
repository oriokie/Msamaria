from flask import render_template, request, redirect, url_for, flash
from app import db
from app.members.models import Member, Dependent
from app.contributions.models import Contribution
from app.cases.models import Case
from sqlalchemy import or_, and_
from flask import Blueprint
from sqlalchemy.sql import func
from app.cases.utils import fetch_member_id, get_member_name, get_dependent_name
from app.finance.models import Expense
import plotly.graph_objs as go
# Define a Blueprint for the contributions route
contributions_bp = Blueprint('contributions', __name__, url_prefix='/contributions')

# Route for searching members and passing active cases
@contributions_bp.route('/search_members', methods=['GET'])
def search_members():
    search_query = request.args.get('search_query')
    if search_query:
        print("Search query:", search_query)  # Debug statement
        
        # We'll use this list to store tuples of (member, matched_name)
        members_with_matches = []

        # Query for members matching the search criteria
        member_matches = Member.query.filter(
            and_(
                Member.active == True,
                or_(
                    Member.name.ilike(f'%{search_query}%'),
                    Member.alias_name_1.ilike(f'%{search_query}%'),
                    Member.alias_name_2.ilike(f'%{search_query}%'),
                    Member.phone_number.ilike(f'%{search_query}%')
                )
            )
        ).all()

        # For each matching member, determine which field matched
        for member in member_matches:
            if search_query.lower() in member.name.lower():
                members_with_matches.append((member, member.name))
            elif member.alias_name_1 and search_query.lower() in member.alias_name_1.lower():
                members_with_matches.append((member, member.alias_name_1))
            elif member.alias_name_2 and search_query.lower() in member.alias_name_2.lower():
                members_with_matches.append((member, member.alias_name_2))
            elif search_query in member.phone_number:
                members_with_matches.append((member, member.name))  # Use name for phone number matches

        # Query for dependents matching the search criteria
        dependent_matches = Dependent.query.filter(
            Dependent.name.ilike(f'%{search_query}%')
        ).all()

        # For each matching dependent, add their associated member
        for dependent in dependent_matches:
            members_with_matches.append((dependent.member, f"{dependent.name} (Dependent of {dependent.member.name})"))

        # Ensure contributions are loaded for each member
        for member, _ in members_with_matches:
            member.contributions

        print("Members found:", members_with_matches)  # Debug statement
    else:
        members_with_matches = []

    active_cases = Case.query.filter_by(closed=False).all()

    # Get paid contributions for each member
    contributions_paid = {}
    for member, _ in members_with_matches:
        contributions_paid[member.id] = [contribution.case_id for contribution in member.contributions if contribution.paid]
    print("Contributions paid:", contributions_paid)  # Debug statement
    print("Active cases:", active_cases)  # Debug statement

    return render_template('search_members.html', members_with_matches=members_with_matches, active_cases=active_cases, contributions_paid=contributions_paid)

# Route for marking contributions as paid or unpaid
@contributions_bp.route('/mark_contribution_paid', methods=['POST'])
def mark_contribution_paid():
    member_id = request.form.get('member_id')
    case_id = request.form.get('case_id')
    print("Member ID:", member_id)  # Debug statement
    print("Case ID:", case_id)  # Debug statement
    contribution = Contribution.query.filter_by(member_id=member_id, case_id=case_id).first()
    if contribution:
        contribution.paid = True
        db.session.commit()
        flash('Contribution marked as paid successfully', 'success')
    else:
        flash('Contribution not found', 'error')
    return redirect(url_for('contributions.search_members'))

# Route for undoing a contribution
@contributions_bp.route('/undo_contribution', methods=['POST'])
def undo_contribution():
    member_id = request.form.get('member_id')
    case_id = request.form.get('case_id')
    print("Member ID:", member_id)  # Debug statement
    print("Case ID:", case_id)  # Debug statement
    contribution = Contribution.query.filter_by(member_id=member_id, case_id=case_id).first()
    if contribution:
        contribution.paid = False
        db.session.commit()
        flash('Contribution payment undone successfully', 'success')
    else:
        flash('Contribution not found', 'error')
    return redirect(url_for('contributions.search_members'))

# # Route for generating contributions for a case
# @contributions_bp.route('/generate_contributions', methods=['POST'])
# def generate_contributions():
#     case_id = request.form.get('case_id')
#     print("Case ID:", case_id)  # Debug statement
#     case = Case.query.get(case_id)
#     if case:
#         generate_contributions_for_case(case)
#         flash('Contributions generated successfully', 'success')
#     else:
#         flash('Case not found', 'error')
#     return redirect(url_for('contributions.search_members'))

# # Function to generate contributions for a case
# def generate_contributions_for_case(case):
#     active_members = Member.query.filter_by(is_deceased=False).all()
#     for member in active_members:
#         contribution = Contribution.query.filter_by(member_id=member.id, case_id=case.id).first()
#         if not contribution:
#             contribution = Contribution(member_id=member.id, case_id=case.id)
#             db.session.add(contribution)
#     db.session.commit()
#     return

# Define a route for the summary page
@contributions_bp.route('/case_summary')
def case_summary():

    # Query database to get information about all cases
    cases = Case.query.all()

    # Initialize a list to store case summaries
    case_summaries = []

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
        total_expenses = total_expenses
        total_amount = total_amount_contributed - total_expenses
        deceased_person = deceased_member

        # Create a dictionary to store case summary information
        case_summary = {
            'id': case.id,
            'deceased_person': deceased_person,
            'total_amount_contributed': total_amount_contributed,
            'active_members_contributed': active_members_contributed,
            'active_members_not_contributed': active_members_not_contributed,
            'total_expenses': total_expenses,
            'total_amount': total_amount,
        }

        # Append the case summary to the list
        case_summaries.append(case_summary)

    # Pass the case summaries to the template for rendering
    return render_template('case_summary.html', case_summaries=case_summaries)


@contributions_bp.route('/case_details/<int:case_id>')
def case_details(case_id):
    # Query the database to get the case with the specified ID
    cases = Case.query.all()
    case = Case.query.get_or_404(case_id)
    
    if case.dependent_id:
        deceased_member = get_dependent_name(case.dependent_id)
    else:
        deceased_member = get_member_name(case.member_id)

    # Get all contributions for the specified case
    contributions = Contribution.query.filter_by(case_id=case_id).all()

    # Initialize lists to store member names and contribution amounts
    member_names = []
    members_not_paid = []

    # Iterate over contributions to gather member names and calculate total contributed amount
    for contribution in contributions:
        member = Member.query.get(contribution.member_id)
        if member and contribution.paid:
            member_names.append(member.name)
        elif member and not contribution.paid:
            members_not_paid.append(member.name)
    
        # Pre-enumerate the member names list
    sorted_member_names = sorted(member_names)
    sorted_members_not_paid = sorted(members_not_paid)
    enumerated_member_names = list(enumerate(sorted_member_names, start=1))
    not_paid_names = list(enumerate(sorted_members_not_paid, start=1))

    number_of_contributions = len(enumerated_member_names)
    total_amount_contributed = number_of_contributions * case.case_amount

    # Pass the case and contribution information to the template for rendering

    # ___________________________PIE CHART______________________________________________________

    # Calculate the counts of active members who have contributed and not contributed to the most recent case
    active_members_contributed = len(set(contribution.member_id for contribution in case.contributions if contribution.paid))
    active_members_not_contributed = len(set(contribution.member_id for contribution in case.contributions if not contribution.paid))

    # Create labels and values for the pie chart
    pie_labels = ['Contributed', 'Not Contributed']
    pie_values = [active_members_contributed, active_members_not_contributed]

    # Create a pie chart
    pie_chart = go.Pie(
        labels=pie_labels,
        values=pie_values,
        hole=0.4,  # Set the size of the center hole
        pull=[0, 0.3]
    )

    # Create layout for the pie chart
    pie_layout = go.Layout(
        title='Distribution of Contributions',
    )

    # Create figure for the pie chart
    pie_fig = go.Figure(data=[pie_chart], layout=pie_layout)

    # Convert pie chart figure to JSON for embedding in HTML
    pie_chart_json = pie_fig.to_json()

    return render_template('case_details.html', case=case,
                           enumerated_member_names=enumerated_member_names,
                            not_paid_names=not_paid_names,
                           deceased_person=deceased_member,
                           total_amount_contributed=total_amount_contributed,
                           pie_chart_json=pie_chart_json,
                           number_of_contributions=number_of_contributions)

