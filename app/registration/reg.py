from flask import render_template, Blueprint, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from app import db
from app.members.models import Member
from app.dependents.models import Dependent

regnew_bp = Blueprint('regnew', __name__)

class MemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    id_number = StringField('ID Number', validators=[DataRequired(), Length(min=12, max=12)])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

@regnew_bp.route('/regnew', methods=['GET', 'POST'])
def register_and_add_dependents():
    form = MemberForm()
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            form = MemberForm(data=data)
            if form.validate():
                try:
                    new_member = Member(
                        name=form.name.data,
                        id_number=form.id_number.data,
                        phone_number=form.phone_number.data,
                        password=form.password.data
                    )
                    db.session.add(new_member)
                    db.session.commit()  # Commit the member first

                    dependents_data = data.get('dependents', [])
                    for dependent_data in dependents_data:
                        new_dependent = Dependent(
                            name=dependent_data['name'],
                            phone_number=dependent_data['phone_number'],
                            relationship=dependent_data['relationship'],
                            member_id=new_member.id
                        )
                        db.session.add(new_dependent)
                    
                    db.session.commit()  # Commit the dependents
                    return jsonify({'success': True, 'message': 'Member and dependents registered successfully'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'success': False, 'message': str(e)})
            else:
                return jsonify({'success': False, 'errors': form.errors})
        else:
            return jsonify({'success': False, 'message': 'Invalid content type, expected JSON'}), 415
    return render_template('registration_form.html', form=form)
