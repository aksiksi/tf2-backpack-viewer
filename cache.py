import json, os
from time import time

def read_from_cache(steamid, folder):
    '''Read response from cache.'''
    with open('cache/{0}/{1}.json'.format(folder, steamid)) as f:
        response = json.load(f)
   
    return response

def write_to_cache(steamid, response, folder):
    '''Add timestamp to response, then write it to cache folder. Return timestamped response.'''
    # Timestamp
    response['time_written'] = time()
    
    # Write response to cache
    with open('cache/{0}/{1}.json'.format(folder, steamid), 'w') as f:
        f.write(json.dumps(response))
    
    return response

def check_in_cache(steamid, folder):
    '''Check if a response is in the cache and is fresh, given a Steam ID and folder.'''
    # Get cache directory contents
    cache = os.listdir('cache/{0}'.format(folder))

    # If response is found, use it. Otherwise, return False.
    for filename in cache:
        if steamid in filename:
            file = filename
            break
    else:
        return False

    with open('cache/{0}/{1}'.format(folder, file)) as f:
        response = json.load(f)

    # Check if response is fresh
    if (time() - int(response['time_written'])) > 259200:
        return False

    return True

if __name__ == '__main__':
    pass