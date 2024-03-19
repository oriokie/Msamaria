from app.dependents.models import Dependent

def fetch_member_id(dependent_id):
    dependent = Dependent.query.get(dependent_id)
    if dependent:
        return dependent.member_id
    else:
        return None
