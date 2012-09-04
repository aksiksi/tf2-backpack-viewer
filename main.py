import sqlite3, requests, json
from flask import Flask, request, url_for, render_template
from parse import *
from time import asctime
     
# App config
DATABASE = '' # Not required yet
DEBUG = True # Set to False once deployed
SECRET_KEY = '' # Use os.urandom()

app = Flask(__name__)
app.config.from_object(__name__)

# Steam API key: must be defined
API_KEY = ''

# Return current date
@app.template_filter('date')
def date():
    now = asctime()
    date = now[4:10] + now[19:]
    return date

# Main page
@app.route('/')
def index():
    return render_template('index.html')

# Search page; parent of result template
@app.route('/search')
def search():
    return render_template('search.html')

# Result retrieval using custom URL
@app.route('/bp/<profile>')
def bp(profile):
    return redirect(url_for('result', s=profile, t='profile'))

# Get search params and pass them to backpack page
@app.route('/result', methods=['GET'])
def result():
    # Start timer
    start = time()

    # Get params
    parameter = request.args.get('s')
    category = request.args.get('t')

    # Find steamid
    steamid = find_steamid(parameter, category)

    # Get responses if steamid is valid
    responses = {'items': None, 'player': None}
    if steamid:
        responses['player'] = get_player_response(steamid, API_KEY)
        responses['items'] = get_item_response(steamid, API_KEY)

    # Get parsed responses
    responses['player'] = parse_player_response(responses['player'])
    responses['items'] = parse_item_response(responses['items'])

    # Add bp_slots to player dict and remove it from item dict
    if responses['player'] and responses['items'] > 0:
        responses['player']['Backpack Slots'] = '{0}/{1}'.format(len(responses['items'][0]), responses['items'].pop(1))

    return render_template('result.html', player=responses['player'], items=responses['items'], time=time()-start)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()