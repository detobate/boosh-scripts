#!/usr/bin/env python3
import requests
import sys,os,signal
import time,datetime
import taglib

# Expects arguments --source-name=live_dj --source-status=false

RECORD_DIR="/home/detonate/boosh_recordings/"
URL="http://stream.boosh.fm:8000/boosh256mp3"
PIDFILE="/tmp/boosh_recording.pid"
CURRENT_URL="http://boosh.fm/current"

def recordStream():
    current = ''
    # Wait until we have the live show name
    while current[:5] != "Live:":
        r = requests.get(CURRENT_URL)
        current = r.text
        time.sleep(3)
    current = current[6:].rstrip() #Strip off the Live: and other fluff at the end

    r = requests.get(URL, stream=True)
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d")
    show = current+" - "+now
    FILENAME = RECORD_DIR+show+".mp3"
    print("Recording: %s" % FILENAME)

    #Create empty file and write id3 tags:
    open(FILENAME, 'a').close()
    update_metadata(FILENAME, show)

    # Open file and 'a'ppend 'b'ytestream after ID3 tag.
    with open(FILENAME, 'ab') as f:
        try:
            for block in r.iter_content(1024):
                f.write(block)
        except:
            print("Couldn't read from %s" % r.url)


def update_metadata(filename, show):
    print("Updating Metadata of %s with %s" % (filename, show))
    file = taglib.File(filename)
    file.tags['TITLE'] = [show]
    file.save()

def main():

    if sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=false" and os.path.isfile(PIDFILE):
        with open(PIDFILE, "r") as p:
            PID=p.readline()
        print("Killing %s" % PID)
        os.kill(int(PID), signal.SIGKILL) # Catching SIGINT gracefully wasn't behaving with the stream
        os.unlink(PIDFILE)

    elif sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=true" and os.path.isfile(PIDFILE):
        print("Error: Already recording.")
        with open(PIDFILE, "r") as p:
            print("PID: %s" % p.readline())
        exit(1)

    elif sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=true" and not os.path.isfile(PIDFILE):
        PID = str(os.getpid())
        print("Creating pid lock file")
        with open(PIDFILE, "w") as f:
            f.write(PID)
        print("Looking for live DJ")
        recordStream()

    elif sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=false" and not os.path.isfile(PIDFILE):
        print("Nothing to do")

    exit(0)



if __name__ == '__main__':
    main()