# Importing the required modules.
from flask import Flask, render_template, session, url_for, redirect
from authlib.integrations.flask_client import OAuth
import json

app= Flask(__name__)

# Creating and registering the app with OAuth server.
oauth=OAuth(app)
app.secret_key='dfhfghdjgh7657656ghtyyu56u'
oauth.register('myapp',
                 redirect_uris="http://localhost:5000/google-login",
                client_id='444835706970-6qjd2gd49bk6hmi2ad3gtgm3cqq3of8b.apps.googleusercontent.com',
                client_secret='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',
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                client_kwargs={
                    'scope':"openid profile email"
                }
               )
# Function to collect all information and storing it in json file.
def dump_session_to_json():
    user_data = session.get('user')
    if user_data:
        with open('user_session.json', 'w') as json_file:
            json.dump(user_data, json_file)

# Function to extract user information from the json file.
def extract_user_info(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            user_info = data.get('userinfo', {})
            email = user_info.get('email', '')
            name = user_info.get('name', '')
            picture_url = user_info.get('picture', '')
            return {'email': email, 'name': name,'picture_url': picture_url}
    except Exception as e:
        print(f"Error reading user session file: {e}")
        return {}


# Function that render the home page of web application.
@app.route('/')
def home():
    user_info = extract_user_info('user_session.json')
    return render_template('index.html', user_info=user_info)

# Function to performe the login task.
@app.route("/login")
def login():
    redirect_uri = url_for("googlecallback", _external=True)
    return oauth.myapp.authorize_redirect(redirect_uri=redirect_uri)

# Function that authorize the user and make connection with user session.
@app.route('/google-login', methods=['GET', 'POST'])
def googlecallback():
    try:
        app.logger.info("Entered googlecallback route")
        token = oauth.myapp.authorize_access_token()
        app.logger.info("Authorization successful")
        session['user'] = token
        dump_session_to_json()
        return redirect(url_for("home"))
     
    except Exception as e:
        app.logger.error(f"Error during Google callback: {e}")
        return f"Error during Google callback: {e}"

# Function that performe the logout task to help the user to logout the user from the current session.
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))   
 
if __name__=="__main__":
    app.run(debug=True, port=5000)