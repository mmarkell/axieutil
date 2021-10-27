from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField


class ProcessClaimsForm(FlaskForm):
    submit = SubmitField('Process Claims')
