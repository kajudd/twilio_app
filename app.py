from flask import Flask, render_template, redirect, session, flash, request, url_for, Response
import model
from sqlalchemy import and_
import forms
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user, login_required
import bcrypt
from twilio.rest import TwilioRestClient
import twilio.twiml
import twilio_config
import datetime
import pytz

app = Flask(__name__)

caller_id = twilio_config.caller_id

default_client = twilio_config.default_client

utc = pytz.timezone("UTC")

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
    if current_user and current_user.is_authenticated:
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

#View that displays contacts.
@app.route("/contacts", methods=["POST", "GET"])
@login_required
def contacts():
    contacts = model.session.query(model.Contact).filter(model.Contact.user_id == current_user.id).all() 
    return render_template("contacts.html", contacts=contacts)

#View to add a new contact.
@app.route("/add_contacts", methods=["POST", "GET"])
@login_required
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


#View to call contact, add new record to database, and update last called.
@app.route('/voice/<int:id>', methods=['GET', 'POST'])
def voice(id):
    account_sid = twilio_config.account_sid
    auth_token = twilio_config.auth_token
    application_sid = twilio_config.application_sid
    current_contact = model.session.query(model.Contact).get(id)
    client = TwilioRestClient(account_sid, auth_token)
    current_contact.last_called = datetime.datetime.utcnow()
    record = model.Record(id=None, contact_id=current_contact.id, 
                            contacted_at=datetime.datetime.utcnow(), confirmation_at=None)
    model.session.add(record)
    model.session.commit()
    call = client.calls.create(to="1" + str(current_contact.phone_number),
                                from_="+19253801536",
                                url='http://%s/greeting/%s' % (request.host, str(record.id)))

    return redirect("/contacts")


#Prompts contact to confirm they are alive.
@app.route('/greeting/<int:id>', methods=['POST'])
def greeting(id):
    resp = twilio.twiml.Response()
    resp.say("Hello, this is Deadman.")
    with resp.gather(numDigits=1, action="/handle-key/%s" % (id), method="POST") as g:
        g.say("To confirm you are alive, press 1.")
    return Response(str(resp), mimetype='text/xml')



@app.route("/handle-key/<int:id>", methods=['GET', 'POST'])
def handle_key(id):
    # Get the digit pressed by the user
    digit_pressed = request.values.get('Digits', None)

    #If user confirms life, update last confirmation and current record.
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
        resp.say("You have confirmed you are alive. Goodbye.")
        record = model.session.query(model.Record).get(id)
        contact_id = record.contact_id
        contact = model.session.query(model.Contact).get(contact_id)
        contact.last_confirmation = datetime.datetime.utcnow()
        record.confirmation_at = datetime.datetime.utcnow()
        model.session.commit()
        return str(resp)
 
    # If the caller pressed anything but 1, let them know they have not confirmed and hang up.
    else:
        resp = twilio.twiml.Response()
        resp.say("You have not confirmed. Goodbye.")   
        return str(resp)

#View to logout.
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
