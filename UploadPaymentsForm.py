from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.simple import SubmitField

class UploadPaymentsForm(FlaskForm):
    file = FileField('Please upload your payments JSON', validators=[FileRequired('Upload a JSON!'), FileAllowed(['json'], 'Upload a JSON!')])
    submit = SubmitField('Submit')
