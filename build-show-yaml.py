#!/usr/bin/env python3
import yaml, html
import requests, ujson

url = "https://admin.boosh.fm/api/week-info"
days = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

def main():
    r = requests.get(url).text
    r = ujson.loads(r)
    temp_yaml = []
    seen = []   # Keep track of show names we've captured
    for day in r:
        if day in days:
            for show in r[day]:
                newshow = {}
                show_name = html.unescape(show['name'])
                if show_name not in seen:
                    seen.append(show_name)
                    newshow['title'] = show_name
                    newshow['picturefile'] = html.unescape(show['name'].lower()) + ".jpg"
                    try:
                        newshow['desc'] = show['description']   #Airtime doesn't actually give us this yet
                    except:
                        newshow['desc'] = None
                    newshow['tags'] = [None]
                    temp_yaml.append(newshow)

    print(yaml.dump(temp_yaml, default_flow_style=False))

if __name__ == "__main__":
    main()