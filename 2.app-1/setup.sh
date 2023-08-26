#!/bin/bash

# Update packages and install necessary ones
sudo yum -y update
sudo yum install -y git python-pip

# Install Flask
pip install Flask

# Create or overwrite the app.py file in the home directory of the ec2-user
cat > /home/ec2-user/app.py <<EOL
# import flask module
from flask import Flask

# instance of flask application
app = Flask(__name__)

# home route that returns below text when root url is accessed
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__': 
   app.run(host='0.0.0.0',port=80)
EOL

# Run Flask app in the background and make it accessible from any IP
cd /home/ec2-user
nohup flask run --host=0.0.0.0 > flask.log 2>&1 &