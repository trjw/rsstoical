#!/usr/bin/python3

from icalendar import Calendar, Event
import feedparser
import datetime
import pytz
import sys

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

def eventUID(event):
    return hashlib.md5(str(event).encode()).hexdigest()

def RssEntryToIcal(rss, cal):
    title=shorten_description(rss['title'])

    summary=shorten_description(rss['summary'])

    date=rss['published_parsed']
    start=datetime.date(date.tm_year,date.tm_mon, 
        date.tm_mday)
    #end=start+timedelta(days=1)
    event=Event()
    event.add('summary',title)
    event.add('description', summary)
    event.add('dtstart', start)
    event.add('uid',"%s" % eventUID(event))
    #event.add('dtend', end)
    #event.add('dtstamp', start)

    cal.add_component(event)


def getCalendar():
    url="https://uq.edu.au/events/rss/event_all_feed.php?cid=16"

    feed=feedparser.parse(url)

    cal=Calendar()
    cal.add('prodid', '-//UQ Academic Calendar//mxm.dk//')
    cal.add('version', '2.0')

    for entry in feed.entries:
        RssEntryToIcal(entry, cal)

    return cal

@app.route('/')
def hello():
    return Response("Hello world\n",mimetype='text/text')

@app.route('/uqacademic.ics')
def serve_ical():
    return Response(cal.to_ical().decode(), mimetype='text/calendar')


if __name__ == "__main__":
    cal = getCalendar()
    print(cal.to_ical().decode())
