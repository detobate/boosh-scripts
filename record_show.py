#!/usr/bin/env python3
import requests
import sys,os,signal
import time,datetime
import eyed3

# Expects arguments --source-name=live_dj --source-status=false

RECORD_DIR="/home/detonate/boosh_recordings/"
URL="http://stream.boosh.fm:8000/boosh256mp3"
PIDFILE="/tmp/boosh_recording.pid"
CURRENT_URL="http://boosh.fm/current"

def recordStream():
    current = ''
    while current[:5] != "Live:":
        r = requests.get(CURRENT_URL)
        current = r.text
        time.sleep(1)
    current = current[6:].rstrip() #Strip off the Live: and other fluff at the end

    r = requests.get(URL, stream=True)
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d")
    FILENAME = RECORD_DIR+current+"-"+now+".mp3"
    print("Recording: %s" % FILENAME)
    with open(FILENAME, 'wb') as f:
        try:
            for block in r.iter_content(1024):
                f.write(block)
        except KeyboardInterrupt:
            os.unlink(PIDFILE)

    writeID3(FILENAME, current)

def writeID3(file, title):
    show = eyed3.load(file)
    show.tag.title = title
    show.tag.save()


def main():

    if sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=false" and os.path.isfile(PIDFILE):
        with open(PIDFILE, "r") as p:
            PID=p.readline()
        print("Killing %s" % PID)
        os.kill(int(PID), signal.SIGTERM)
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
        print("Starting recording")
        recordStream()
        os.unlink(PIDFILE)

    elif sys.argv[1] == "--source-name=live_dj" and sys.argv[2] == "--source-status=false" and not os.path.isfile(PIDFILE):
        print("Nothing to do")

    exit(0)



if __name__ == '__main__':
    main()