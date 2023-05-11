from google.oauth2 import id_token
from google.auth.transport import requests
import os

CLIENT_ID = '707081518512-efqnpuod4o1aoqnd8un716s67i5g71i3.apps.googleusercontent.com'

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, Request(), CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
        # Extract the user's information
        user_info = {
            'id': idinfo['sub'],
            'name': idinfo['name'],
            'email': idinfo['email'],
            'picture': idinfo['picture']
        }
        return user_info
    except ValueError:
        # Invalid token
        return None
    
from flask import Flask, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv('GOOG_OAUTH_CLIENT_SECRET')

@app.route('/login/google/callback')
def google_callback():
    code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_params = {
        'code': code,
        'client_id': '707081518512-efqnpuod4o1aoqnd8un716s67i5g71i3.apps.googleusercontent.com',
        'client_secret': os.getenv('GOOG_OAUTH_CLIENT_SECRET'),
        'redirect_uri': 'https://grounded-datum-379919.firebaseapp.com/__/auth/handler',
        'grant_type': 'authorization_code'
    }
    # Exchange the authorization code for an access token
    response = requests.post(token_url, data=token_params)
    token = response.json().get('id_token')
    # Verify the authentication token
    user_info = verify_google_token(token)
    if user_info:
        # User is authenticated, store the user's information in the session
        session['user'] = user_info
        return redirect(url_for('dashboard'))
    else:
        # Authentication failed
        return redirect(url_for('login'))