from wtforms import Form, BooleanField, TextField, TextAreaField, validators   


class QuestionForm(Form):
    question = TextAreaField('Your answer', [validators.Length(min=2, max=85, message='Your answer should be between 2 and 85 characters long.')])


class EmailForm(Form):
    email = TextField('Your email address', [validators.Email(message='Check that your email address is right')])

