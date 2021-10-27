from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.simple import SubmitField



class UploadPrivateKeysForm(FlaskForm):
    file = FileField('Please upload your private keys CSV', validators=[FileRequired('Upload a CSV!'), FileAllowed(['csv'], 'Upload a CSV!')])
    submit = SubmitField('Submit')
