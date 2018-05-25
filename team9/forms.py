from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, SubmitField

from wtforms.validators import DataRequired, Email, ValidationError, InputRequired, Required

from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddMatch(FlaskForm):
    # TODO Dynamic pick list based on history
    teampick = SelectField('Pick Team', choices=[('1','Niners'), ('2','I Rack, I Ran')], coerce=int)
    opposingteam = StringField('Opposing Team', validators=[DataRequired()])
    # TODO Revisit 'flask-moment' extention from'Dates and Times' section
    matchdate = DateField('Match Date', validators=[DateField], default=datetime.today() , format="%Y-%m-%d")
    submit = SubmitField('Create Match')