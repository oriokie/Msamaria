from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Regexp

class DependentForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(min=1, max=255)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(min=1, max=15)])
    relationship = StringField('Relationship', validators=[Optional(), Length(min=1, max=255)])

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=1, max=255)])
    id_number = StringField('ID Number', validators=[DataRequired(), Length(min=1, max=12)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=1, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    reg_fee_paid = BooleanField('Registration Fee Paid')
    is_admin = BooleanField('Admin')
    is_deceased = BooleanField('Deceased')
    dependents = FieldList(FormField(DependentForm), min_entries=0)
    submit = SubmitField('Register')
