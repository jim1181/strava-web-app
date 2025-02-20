import os
from flask import Flask, redirect, request, session, url_for
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Strava API credentials (replace with your own)
CLIENT_ID = '149188'  # Replace with your Strava app's Client ID
CLIENT_SECRET = '38e66c0141e6e85a569cf67f97cb651bd4aba5e0'  # Replace with your Strava app's Client Secret
REDIRECT_URI = 'http://localhost:5000/callback'  # For local testing; update when deployed

# OAuth endpoints
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
API_URL = "https://www.strava.com/api/v3/athlete/activities"

@app.route('/')
def home():
    return 'Welcome to Strava Data Fetcher! Go to /login to authenticate.'

@app.route('/login')
def login():
    # Redirect to Strava OAuth page for user authentication
    auth_url = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=read,activity:read"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the URL
    auth_code = request.args.get('code')

    # Exchange the authorization code for an access token
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
    }
    
    # Request access token
    response = requests.post(TOKEN_URL, data=payload)
    data = response.json()
    
    # Save the access token in the session
    session['access_token'] = data['access_token']
    
    return redirect(url_for('fetch_data'))

@app.route('/fetch_data')
def fetch_data():
    # Check if we have a valid access token
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    access_token = session['access_token']
    
    # Fetch Strava activities using the access token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        activities = response.json()
        return f"Activities: {activities}"
    else:
        return "Failed to fetch data from Strava."

if __name__ == '__main__':
    app.run(debug=True)
