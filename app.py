import os
from flask import Flask, redirect, request, session, url_for
import requests
import pandas as pd  # Don't forget to import pandas for CSV saving!

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Strava API credentials (replace with your own)
CLIENT_ID = '149188'  # Replace with your Strava app's Client ID
CLIENT_SECRET = '38e66c0141e6e85a569cf67f97cb651bd4aba5e0'  # Replace with your Strava app's Client Secret
REDIRECT_URI = 'https://strava-web-app.onrender.com/callback'  # For local testing; update when deployed

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
    
    return redirect(url_for('fetch_activities'))  # Redirect to fetch_activities route

@app.route('/fetch_activities')
def fetch_activities():
    # Check if we have a valid access token
    if 'access_token' not in session:
        return redirect(url_for('login'))  # Redirect to login if no access token
    
    access_token = session['access_token']
    
    # Fetch all Strava activities using the access token
    activities = fetch_all_strava_data(access_token)
    
    if activities:
        save_to_csv(activities)  # Optionally save them to CSV
        return f"{len(activities)} activities fetched and saved to CSV."
    else:
        return "Failed to fetch data from Strava or no activities found."

# Function to fetch activities with pagination
def fetch_all_strava_data(access_token, per_page=200):
    all_activities = []  # List to hold all activities
    page = 1  # Start with the first page
    
    while True:
        try:
            url = 'https://www.strava.com/api/v3/athlete/activities'
            headers = {'Authorization': f'Bearer {access_token}'}  # Authorization header
            params = {'per_page': per_page, 'page': page}  # API parameters
            
            # Send GET request to Strava API
            response = requests.get(url, headers=headers, params=params)
            
            # Check if response is valid
            if response.status_code == 200:
                data = response.json()  # Convert the response to a JSON format (list of activities)
                if not data:  # If no more data is returned (empty list), stop the loop
                    break
                all_activities.extend(data)  # Add the activities to the list
                page += 1  # Move to the next page
            else:
                # Log response status and content for debugging
                print(f"Error fetching data: {response.status_code} - {response.text}")
                break
        
        except Exception as e:
            print(f"Exception occurred while fetching activities: {e}")
            break
    
    return all_activities  # Return the list of all activities

# Optional: Save activities to a CSV file using pandas
def save_to_csv(activities, filename='activities.csv'):
    df = pd.DataFrame(activities)  # Convert the list of activities to a pandas DataFrame
    df.to_csv(filename, index=False)  # Save the DataFrame to a CSV file
    print(f"Saved {len(activities)} activities to {filename}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
