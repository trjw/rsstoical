#!/usr/bin/python3

from icalendar import Calendar, Event
import feedparser
import datetime
import pytz
import sys

def display(cal):
    return cal.to_ical().decode().replace('\r\n', '\n').strip()

def shorten_description(text):
    abbrev={"Examination":"Exam", "Semester":"Sem", "Quarter":"Qtr", "Research":"Rsch"}
    tmp=text
    for a in abbrev:
        tmp=tmp.replace(a,abbrev[a])
    return tmp

def rsstoical(rss, uid, cal):
    title=shorten_description(rss['title'])

    summary=shorten_description(rss['summary'])

    date=rss['published_parsed']
    start=datetime.date(date.tm_year,date.tm_mon, 
        date.tm_mday)
    #end=start+timedelta(days=1)
    event=Event()
    event.add('summary',title)
    event.add('description', summary)
    event.add('uid',"%i" % uid)
    event.add('dtstart', start)
    #event.add('dtend', end)
    #event.add('dtstamp', start)

    cal.add_component(event)

url="https://uq.edu.au/events/rss/event_all_feed.php?cid=16"

feed=feedparser.parse(url)

cal=Calendar()
cal.add('prodid', '-//My Calendar product//mxm.dk//')
cal.add('version', '2.0')

uid=1
for entry in feed.entries:
    rsstoical(entry, uid, cal)
    uid+=1

print(cal.to_ical().decode())


