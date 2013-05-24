from flask_wtf import Form, TextField, PasswordField, IntegerField
from flask_wtf import Required, validators


class RegistrationForm(Form):
    name = TextField('Name', [validators.Length(min=1, max=25)])
    email = TextField('Email', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [Required()])


class LoginForm(Form):
    email = TextField('Email', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [Required()])


class ContactForm(Form):
    first_name = TextField('First Name', [validators.Length(min=1, max=140)])
    last_name = TextField('Last Name', [validators.Length(min=1, max=140)])
    phone_number = TextField('Phone Number', [validators.Length(min=10, max=10)])