from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Here is the server for the heating controller.   See the site here...'


@app.route('/temp')
def temp():
	
    return jsonify('Here is the server for the heating controller.   See the site here...')
