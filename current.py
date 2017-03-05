#!/usr/bin/env python3

import requests
import json
import time
from collections import deque


url = "https://admin.boosh.fm/api/live-info"
playlist = "/var/log/icecast2/playlist.log"
output = "/var/www/boosh.fm/current"

def getCurrentSong():
    ''' Replace this with a call to Icecast once it's been upgraded to 2.4.0
        and can spit out JSON '''
    with open(playlist, 'r', errors='ignore') as f:
        q = deque(f, 1).pop().split('|')
        return(q[len(q)-1].rstrip())

def checkLive():
    results = requests.get(url)
    try:
        results = json.loads(results.text)
    except:
        exit(1)

    return(results)


def main():

    while True:

        results = checkLive()
        live = results['livedj']

        if live == "off":
            current = getCurrentSong()
        elif live == "on":
            current = "Live: " + results['currentShow'][0]['name']

        with open(output, 'w') as f:
            f.write(current)

        time.sleep(5)


if __name__ == "__main__":
    main()