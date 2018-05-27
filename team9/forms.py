from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, InputRequired, Required

# Database Items
from team9 import db
from team9.models import Match

from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddMatch(FlaskForm):
    i=0
    picks=[]
    picks.append((0,'New Team..'))
    teams = db.session.query(Match.OpposingTeam).group_by(Match.OpposingTeam).order_by(Match.OpposingTeam).all()
    for team in teams:
        i=i+1
        picks.append((i,team.OpposingTeam))
    teampick = SelectField('Pick Team', choices=picks, coerce=int)
    opposingteam = StringField('Opposing Team')
    playoff = BooleanField('Playoff Match')
    # TODO Revisit 'flask-moment' extension from'Dates and Times' section
    matchdate = DateField('Match Date', validators=[DateField], default=datetime.today() , format="%Y-%m-%d")
    submit = SubmitField('Create Match')


    def validate_opposingteam(self, opposingteam):
        # 0 means 'New team..'
        if self.teampick.data==0:
            if len(self.opposingteam.data)==0:
                raise ValidationError('Select Opposing Team from list or Enter a team name in the text box.')