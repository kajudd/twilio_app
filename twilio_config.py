from twilio.util import TwilioCapability

def client():
    """Respond to incoming requests."""
 
    account_sid = "AC3b6c85a38bdca4daec6aab5ee95bdaea"
    auth_token = "cb6ad97c390cc50e30ba7d41f300574a"
 
    # This is a special Quickstart application sid - or configure your own
    # at twilio.com/user/account/apps
    application_sid = "AP89f94c23cb30bf448e9d118e00ce1f2c"
 
    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    token = capability.generate()
	return render_template('client.html', token=token)