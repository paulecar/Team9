from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, widgets


class Message(FlaskForm):
    # Message text added to weekly / new match mime email
    weekly_message = TextAreaField('Message', render_kw={"rows": 10, "cols": 30})
    submit = SubmitField('Update Message')

