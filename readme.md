# Checkup

An app using the Twilio API. Checkup allows you to enter contacts, and call your contacts from the browser.

It uses TwiML text to speech to ask your contact to confirm they are okay by pressing one.

If the contact confirms, Checkup displays the time of the last confirmation in addition to the time of the last call.

To use: clone the project, add a config file with your twilio account information, insert the phone number of your choice as a string where noted in app.py, deploy or expose your local host to receive requests from Twilio.

*Features*

* Login service
* Add contacts
* Call contacts from the browser
* Dashboard to manage contacts
* Text to speech calling via Twilio API
* Updates with time that the contact last confirmed their status.

*Project*

![alt text](https://github.com/kjudd/checkup/raw/master/static/img/readme1.png "Login Screen")

![alt text](https://github.com/kjudd/checkup/raw/master/static/img/readme2.png "Contacts Dashboard")
