import sqlite3, requests, json
from flask import Flask, request, session, g, redirect, \
     abort, url_for, render_template, flash
from database import *
from parse import *
from time import time, asctime
     
# App config
DATABASE = '' # Not required yet
DEBUG = True # Set to False once deployed
SECRET_KEY = '' # Use os.urandom()

app = Flask(__name__)
app.config.from_object(__name__)

# Steam API key: must be defined
API_KEY = ''

# Current date
now = asctime()
date = now[4:10] + now[19:]

# Main page
@app.route('/')
def index():
    return render_template('index.html', date=date)

# Search page; parent of result template
@app.route('/search')
def search():
    return render_template('search.html', date=date)

# Show results
@app.route('/result', methods=['GET'])
def result():
    # Start timer
    start = time()
    
    # Get form parameters
    parameter = request.args.get('s')
    type = request.args.get('t')

    # Find steamid
    steamid = find_steamid(parameter, type)

    # Get responses if steamid is valid
    responses = {'item': None, 'player': None}
    if steamid:
        responses['player'] = get_player_response(steamid, API_KEY)
        responses['item'] = get_item_response(steamid, API_KEY)

    # Get parsed responses
    responses['player'] = parse_player_response(responses['player'])
    responses['item'] = parse_item_response(responses['item'])

    # Add bp_slots to player dict and remove it from item dict if player and item data is valid
    if responses['player'] and responses['item'] > 0:
        responses['player'][0]['Backpack Slots'] = '{0}/{1}'.format(len(responses['item'][0]), responses['item'].pop(1))

    return render_template('result.html', player=responses['player'], items=responses['item'], time=time()-start, date=date)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()