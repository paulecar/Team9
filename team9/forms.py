from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, SubmitField

from wtforms.validators import DataRequired, Email, ValidationError, InputRequired, Required

import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired])
    password = StringField('Password', validators=[DataRequired])
    remember = StringField('Remember Me', validators=[BooleanField])
    submit = SubmitField('Sign In')

class AddMatch(FlaskForm):
    # TODO Dynamic pick list based on history
    teampick = SelectField('Pick Team', choices=['Niners','I Rack, I Ran'], coerce=int)
    opposingteam = StringField('Opposing Team', validators=[DataRequired])
    matchdate = DateField('Match Date', validators=[DateField], default=datetime.today, format="%Y-%m-%dT")
    submit = SubmitField('Create Match')