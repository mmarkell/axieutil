from flask_wtf import FlaskForm
from wtforms.fields.core import StringField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired

class UploadPrivateKeysForm(FlaskForm):
    seed_phrase = StringField('Please enter your seed phrase', validators=[DataRequired("This is a required field")])
    submit = SubmitField('Submit (this may take a while)')
