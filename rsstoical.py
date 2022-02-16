#!/usr/bin/python3

from icalendar import Calendar, Event
import feedparser
import datetime
import pytz
import sys
import re
import hashlib

from flask import Flask, Response

app = Flask(__name__)

def display(cal):
    return cal.to_ical().decode().replace('\r\n', '\n').strip()

def shorten_description(text):
    abbrev={"Examination":"Exam", "examination":"exam", "Semester":"Sem", "Quarter":"Qtr"}
    tmp=text
    for a in abbrev:
        tmp=tmp.replace(a,abbrev[a])
    return tmp

"""
Generate a unique UID for an event by hashing the event details
"""
def eventUID(event):
    return hashlib.md5(str(event).encode()).hexdigest()

def RssEntryToIcal(rss, cal):
    title=shorten_description(rss['title'])

    summary=shorten_description(rss['summary'])

    date=rss['published_parsed']
    start=datetime.datetime(date.tm_year, date.tm_mon, date.tm_mday)
    #end=start+timedelta(days=1)
    event=Event()
    event.add('summary',title)
    event.add('description', summary)
    event.add('dtstamp', datetime.datetime.today())
    event.add('dtstart', start)

    event.add('uid',"%s" % eventUID(event))

    cal.add_component(event)


# Round a date back to the Monday of that week
def mondayOfWeek(dt):
    return dt + datetime.timedelta(days=-dt.weekday())

def decodeTeachingWeeks(cal, sem):
    events = cal.walk('VEVENT')

    semStr = "Sem " + sem
    for event in events:
        if "DESCRIPTION" in event:
            descr = event['DESCRIPTION']
            if (re.search(semStr + " classes commence", descr)):
                semStart = mondayOfWeek(event['DTSTART'].dt)
                #print(descr)

            if (re.search(semStr + " classes end before mid-semester break", descr)):
                semPause = event['DTSTART'].dt
                #print(descr)

            if(re.search(semStr + " classes recommence after mid-semester break", descr)):
                semRestart = mondayOfWeek(event['DTSTART'].dt)
                #print(descr)

            if(re.search(semStr + " classes end", descr)):
                semEnd = event['DTSTART'].dt
                #print(descr)

    #print("start", semStart, "pause", semPause, "restart", semRestart, "end", semEnd)

    # Convert restart to the monday of that week
    week = 1
    semester = 1
    weekStart = semStart
    while weekStart <= semEnd:
        # Skip the mid-semester break
        if(weekStart >= semPause and weekStart < semRestart):
            weekStart = weekStart + datetime.timedelta(weeks=1)
            continue

        # Ceraet a VEVENT
        title="Week " + str(week)
        summary = title;

        event=Event()
        event.add('summary',title)
        event.add('description', summary)
        event.add('dtstamp', datetime.datetime.today())
        event.add('dtstart', weekStart)
        event.add('uid',"%s" % eventUID(event))

        cal.add_component(event)

        #print("Week", week,weekStart)
        week = week + 1
        weekStart = weekStart + datetime.timedelta(weeks=1)
        


def getCalendar():
    url="https://uq.edu.au/events/rss/event_all_feed.php?cid=16"

    feed=feedparser.parse(url)

    cal=Calendar()
    cal.add('prodid', '-//UQ Academic Calendar//mxm.dk//')
    cal.add('version', '2.0')

    for entry in feed.entries:
        RssEntryToIcal(entry, cal)

    decodeTeachingWeeks(cal, "1")
    decodeTeachingWeeks(cal, "2")

    return cal

@app.route('/')
def hello():
    return Response("Subscribe to webcals://uqcal.uqcloud.net/uqacademic.ics" ,mimetype='text/text')

@app.route('/uqacademic.ics')
def serve_ical():
    cal = getCalendar()
    return Response(cal.to_ical().decode(), mimetype='text/calendar')

if __name__ == "__main__":
    cal = getCalendar()
    print(cal.to_ical().decode())
