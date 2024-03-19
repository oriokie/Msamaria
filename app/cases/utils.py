from app.dependents.models import Dependent
from app.members.models import Member

def fetch_member_id(dependent_id):
    dependent = Dependent.query.get(dependent_id)
    if dependent:
        return dependent.member_id
    else:
        return None

def get_member_name(member_id):
    member = Member.query.get(member_id)
    return member.name if member else None

def get_dependent_name(dependent_id):
    dependent = Dependent.query.get(dependent_id)
    return dependent.name if dependent else None
