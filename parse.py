import sqlite3, requests, json, os, re
import xml.etree.ElementTree as etree
from collections import OrderedDict
from cache import *
from time import time, ctime

def from_normal_to_64(steamid):
    '''Convert Steam ID of format STEAM_X:Y:Z to 64-bit Steam Community ID. Refer to https://developer.valvesoftware.com/wiki/SteamID.'''
    Y, Z = re.findall(u':(\w+):(\w+)', steamid)[0]
    V = 0x0110000100000000
    steamid64 = int(Z) * 2 + V + int(Y)
    return steamid64

def from_profile_to_64(steamid):
    '''Get the username of a given Steam ID using XML option in Steam Profile.'''
    # In case input returns an invalid webpage
    try:
        doc = requests.get('http://steamcommunity.com/id/{0}/?xml=1'.format(steamid)).text.encode('utf-8')
        xml = etree.fromstring(doc)
        steamid64 = xml.findtext('steamID64')
    except:
        return None
    
    return steamid64

def get_player_response(steamid, API_KEY, folder='players'):
    '''Get player response from Steam API, if it doesn't already exist in cache.'''
    in_cache = check_in_cache(steamid, folder)

    # Return cached response if it is already in the cache
    if in_cache:
        response = read_from_cache(steamid, folder)
        return response

    # Otherwise grab response using Steam API
    text = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?steamids={0}&key={1}'. \
                         format(steamid, API_KEY)).text.encode('UTF-8') # Make sure it's UTF-8
    response = json.loads(text)['response']

    # Write response to cache if it contains data
    if response['players']:
        return write_to_cache(steamid, response, folder)

    return None

def get_item_response(steamid, API_KEY, folder='items'):
    '''Get item response from Steam API, if it doesn't already exist in cache.'''
    in_cache = check_in_cache(steamid, folder)

    # Return cached response if it is already in the cache
    if in_cache:
        response = read_from_cache(steamid, folder)
        return response

    # Otherwise grab response using Steam API
    text = requests.get('http://api.steampowered.com/ITFItems_440/GetPlayerItems/v0001/?steamID={0}&key={1}'. \
                         format(steamid, API_KEY)).text.encode('UTF-8') # Make sure it's UTF-8
    response = json.loads(text)['result']

    # Write response to cache if it exists and contains items
    status = response['status']
    if status == 1 and None not in response['items']['item']:
        return write_to_cache(steamid, response, folder)
    elif status == 8 or status == 18:
        return None
    elif status == 15:
        return -1
    elif None in response['items']['item']:
        return -2

def find_steamid(parameter, type):
    '''Find 64-bit Steam ID based on passed parameter.'''
    if ('765611980' in parameter and len(parameter) == 17) and type == 'steamid64':
        steamid64 = parameter
    elif 'STEAM_' in parameter and type == 'steamid':
        # Make sure it's not just a customURL
        try:
            steamid64 = from_normal_to_64(parameter)
        except: 
            steamid64 = from_profile_to_64(parameter)
    elif parameter and type == 'profile':
        steamid64 = from_profile_to_64(parameter)
    else:
        return False

    # Make sure steamid64 exists
    if steamid64:
        return steamid64
    
    return False

def replace_item_names(parsed_items):
    '''Change the names of items that aren't adequately named in the schema.'''
    item_names = {
        'Upgradeable TF_WEAPON_BAT': 'Bat',
        'Upgradeable TF_WEAPON_BOTTLE': 'Bottle',
        'Upgradeable TF_WEAPON_FIREAXE': 'Fireaxe',
        'Upgradeable TF_WEAPON_CLUB': 'Club',
        'Upgradeable TF_WEAPON_KNIFE': 'Knife',
        'Upgradeable TF_WEAPON_FISTS': 'Fists',
        'Upgradeable TF_WEAPON_SHOVEL': 'Shovel',
        'Upgradeable TF_WEAPON_WRENCH': 'Wrench',
        'Upgradeable TF_WEAPON_BONESAW': 'Bonesaw',
        'Upgradeable TF_WEAPON_SHOTGUN_PRIMARY': 'Shotgun',
        'Upgradeable TF_WEAPON_SCATTERGUN': 'Scattergun',
        'Upgradeable TF_WEAPON_SNIPERRIFLE': 'Sniper Rifle',
        'Upgradeable TF_WEAPON_MINIGUN': 'Minigun',
        'Upgradeable TF_WEAPON_SMG': 'Submachinegun',
        'Upgradeable TF_WEAPON_SYRINGEGUN_MEDIC': 'Syringe Gun',
        'Upgradeable TF_WEAPON_ROCKETLAUNCHER': 'Rocket Launcher',
        'Upgradeable TF_WEAPON_GRENADELAUNCHER': 'Grenade Launcher',
        'Upgradeable TF_WEAPON_PIPEBOMBLAUNCHER': 'Stickybomb Launcher',
        'Upgradeable TF_WEAPON_FLAMETHROWER': 'Flamethrower',
        'Upgradeable TF_WEAPON_PISTOL': 'Pistol',
        'Upgradeable TF_WEAPON_REVOLVER': 'Revolver',
        'Upgradeable TF_WEAPON_MEDIGUN': 'Medigun',
        'Upgradeable TF_WEAPON_INVIS': 'Inviswatch',
        'Upgradeable TF_WEAPON_BUILDER_SPY': 'Sapper',
        'Upgradeable TF_WEAPON_PDA_ENGINEER_BUILD': 'PDA',
        'Craft Bar Level 1': 'Scrap Metal',
        'Craft Bar Level 2': 'Reclaimed Metal',
        'Craft Bar Level 3': 'Refined Metal',
        'TTG Max Pistol - Poker Night': 'Lugermorph',
        'OSX Item': 'Earbuds',
        'Treasure Hat 1': 'Bounty Hat',
        'Treasure Hat 2': 'Treasure Hat'
        }
    
    for item in parsed_items[1:]:
        name = item['Name']
        if name in item_names:
            item['Name'] = item_names[name]
    
    return parsed_items

def parse_item_response(response):
    '''Extract what's needed from the JSON response and use the TF2 item schema to get new data.'''
    # Get item schema from JSON file.
    with open('json/schema.json') as f:
        tf2_item_schema = OrderedDict(json.load(f))['result'] # Keep everything in order
    
    # Check variables and results
    if response <= 0:
        return response
    
    # Variables..
    ordered_response = OrderedDict(response)
    items_in_bp = ordered_response['items']['item']
    schema_items = tf2_item_schema['items']
    bp_slots = ordered_response['num_backpack_slots']
    time_written = ctime(ordered_response['time_written']) # Timestamp in ASCII form
    item_qualities = {v:k.title() for k, v in tf2_item_schema['qualities'].items()} # Reverse dict to make searching easier
    item_origins = {each['origin']:each['name'] for each in tf2_item_schema['originNames']} # Map origin number to name
    req = [
        ('image_url', 'Image'),
        ('name', 'Name'),
        ('level', 'Level'),
        ('defindex', 'Identifier'),
        ('flag_cannot_trade', 'Tradeable?'),
        ('flag_cannot_craft', 'Craftable?'),
        ('quantity', 'Quantity'),
        ('quality', 'Quality'),
        ('origin', 'Origin'),
        ('id', 'ID'),
        ('original_id', 'Original ID'),
        ('custom_name', 'Custom Name'),
        ('custom_desc', 'Custom Description'),
    ]

    # Make a dictionary mapping of item defindex to absolute index in list -> {defindex: index}
    mapping = {item['defindex']:schema_items.index(item) for item in schema_items}
    
    parsed_items = [] # Item dicts stored here
    
    # Get required info from each item; use mapping to find each item in JSON response
    for item in items_in_bp:
        current_item = OrderedDict() # Empty ordered dict for each item
        
        # Used to find item position in schema through mapping
        current_index = mapping[item['defindex']]
        
        # Check if each attribute is in either the schema or the item response, and add to current_item if it is
        for pair in req:
            attr = pair[0]
            new_attr = pair[1]
            if attr in item:
                if attr == 'quality':
                    quality = item_qualities[item[attr]]
                    if quality == 'Rarity1':
                        current_item[new_attr] = 'Genuine'
                    elif quality == 'Rarity4':
                        current_item[new_attr] = 'Unusual'
                    elif quality == 'Selfmade':
                        current_item[new_attr] = 'Self-Made'
                    else:
                        current_item[new_attr] = quality
                elif attr == 'origin':
                    current_item[new_attr] = item_origins[item[attr]]
                elif attr == 'flag_cannot_trade' or attr == 'flag_cannot_craft':
                    current_item[new_attr] = 'No'
                else:
                    current_item[new_attr] = item[attr]
            elif attr in schema_items[current_index]:
                current_item[new_attr] = schema_items[current_index][attr]
            else:
                if attr == 'flag_cannot_trade' or attr == 'flag_cannot_craft':
                    current_item[new_attr] = 'Yes'
                elif attr == 'custom_name' or attr == 'custom_desc':
                    current_item[new_attr] = 'None'
        
        parsed_items.append(current_item) # Append each item to parsed_items
        
    replaced_items = replace_item_names(parsed_items)
        
    return [replaced_items, bp_slots, time_written]

def parse_player_response(response):
    '''Convert player response into a dict containing required info.'''
    # Check if response exists
    if not response:
        return None

    # Variables..
    player_info = response['players'][0]
    time_written = ctime(response['time_written'])
    ordered_response = OrderedDict()
    req = [
        ('personaname', 'Profile Name'),
        ('avatarmedium', 'Avatar'),
        ('steamid', 'Steam ID'),
        ('realname', 'Real Name'),
        ('personastate', 'Status'),
        ('lastlogoff', 'Last Logoff'),
        ('timecreated', 'Account Creation Date'),
        ('profileurl', 'Profile')
    ]
    status = ['Offline', 'Online', 'Busy', 'Away', 'Snooze', 'Looking to Trade', 'Looking to Play']

    # Populate ordered_response with player info; if entry is time-related, convert time to ASCII format
    for pair in req:
        key = pair[0]
        new_key = pair[1]
        if key in player_info:
            if key == 'lastlogoff' or key == 'timecreated':
                ordered_response[new_key] = ctime(player_info[key])
            elif key == 'personastate': # Get user status]
                ordered_response[new_key] = status[player_info[key]]
            else:
                ordered_response[new_key] = player_info[key]
        else:
            if key == 'realname':
                ordered_response[new_key] = 'Not listed'

    return [ordered_response, time_written]

if __name__ == '__main__':
    pass