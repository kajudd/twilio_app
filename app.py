from flask import Flask, render_template, redirect, session, flash, request
import model
from sqlalchemy import and_
import forms
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user, login_required
import bcrypt
from twilio.util import TwilioCapability
import twilio.twiml
import re
import twilio_config

app = Flask(__name__)

caller_id = twilio_config.caller_id

default_client = twilio_config.default_client

#Set up config for WTForms CSRF.
app.config.from_object('config')

#Set up login manager for Flask-Login.
lm = LoginManager()
lm.setup_app(app)

#Login manager setup for Flask-Login.
@lm.user_loader
def load_user(id):
    return model.session.query(model.User).get(int(id))

#View to login 
@app.route("/", methods=["POST", "GET"])
def login():
    form = forms.LoginForm()
    #If user is already in session, redirect to choose game.
    if current_user is not None and current_user.is_authenticated():
        return redirect("/contacts")
    #Login view to allow user to log in, compares given password to salted password.
    login_form = forms.LoginForm()
    if login_form.validate_on_submit():
        user = model.session.query(model.User).filter_by(email=login_form.email.data).first()
        if user is None:
            flash('Invalid login. Please try again.')
            return redirect('/')
        elif bcrypt.hashpw(login_form.password.data, user.password) == user.password:
                login_user(user)
                return redirect("/contacts")
        else:
            flash('Invalid password. Please try again.')
            return redirect('/')
    else:
        return render_template("login.html", form=form)

#View to sign up.
@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    #Sign up view to add player id, name, email, and hashed password to database.
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        email_query = model.session.query(model.User).filter_by(email=form.email.data).all()
        hashed = bcrypt.hashpw(form.password.data, bcrypt.gensalt(10))
        if not email_query:
            user = model.User(id=None, name=form.name.data, email=form.email.data,
                                  password=hashed)
            model.session.add(user)
            model.session.commit()
            login_user(user)
            return redirect("/contacts")
        else:
            flash('Account exists. Please log in.')
            return redirect('/sign_up')
    else:
        return render_template("sign_up.html", form=form)


@app.route("/contacts", methods=["POST", "GET"])
@login_required
def contacts():
#MAKE PAGE THAT DISPLAYS ALL CONTACTS WITH BUTTONS TO CALL
    ##CONTACTS ARE ALL THE USER'S CONTACTS AND THE INFO ABOUT THEM
    #GO THROUGH THE CONTACTS AND FOR EACH CONTACT, FILL IN THE CHARTS WITH THOSE THINGS

    ##FIRST NAME, LAST NAME, PHONE NUMBER, LAST CALLED, LAST CONFIRMATION
    contacts = model.session.query(model.Contact).filter(model.Contact.user_id == current_user.id).all() 
    return render_template("contacts.html", contacts=contacts)

@app.route("/add_contacts", methods=["POST", "GET"])
@login_required
#MAKE A PAGE THAT LETS YOU ADD A NEW CONTACT, LINKED TO FROM CONTACTS
def add_contacts():
    form = forms.ContactForm()
    if form.validate_on_submit():
        number_query = model.session.query(model.Contact).filter(and_(model.Contact.user_id == current_user.id,
                                                                    model.Contact.phone_number == form.phone_number.data)).all()
        if not number_query:
            contact = model.Contact(id=None, user_id=current_user.id, first_name=form.first_name.data,
                                    last_name=form.last_name.data, phone_number=form.phone_number.data,
                                    last_called=None, last_confirmation=None)
            model.session.add(contact)
            model.session.commit()
            return redirect("/contacts")
        else:
            flash('Phone number is attached to another contact.')
            return redirect('/add_contacts')
    else:
        return render_template("add_contacts.html", form=form)


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    from_number = request.values.get('PhoneNumber', None)
 
    resp = twilio.twiml.Response()
 
    with resp.dial(callerId=caller_id) as r: 
        # If we have a number, and it looks like a phone number:
        if from_number and re.search('^[\d\(\)\- \+]+$', from_number):
            r.number(from_number)
        else:
            r.client(default_client)
 
    return str(resp)

# @app.route("/delete_contact")
# #GIVES YOU A LIST OF CONTACTS, CLICK ON THE ONE YOU WANT TO DELETE
@app.route('/client', methods=['GET', 'POST'])
@login_required
def client():
    """Respond to incoming requests."""
    account_sid = twilio_config.account_sid
    auth_token = twilio_config.auth_token
    # This is a special Quickstart application sid - or configure your own
    # at twilio.com/user/account/apps
    application_sid = twilio_config.application_sid
    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    capability.allow_client_incoming(default_client)
    token = capability.generate()
    return render_template('client.html', token=token)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
