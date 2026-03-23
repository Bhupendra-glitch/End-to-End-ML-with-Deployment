import pyrebase
from config.firebase_config import firebase_config

# Initialize Firebase app using config
firebase = pyrebase.initialize_app(firebase_config)

# Create auth object (used for login/signup)
auth = firebase.auth()
