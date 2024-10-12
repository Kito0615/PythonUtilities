#! /usr/bin/env python3
# -*- encoding:utf-8 -*-
#
# Author: Anar(anar930906@gmail.com)
# File: iCalCreator.py
#

import csv
import icalendar
from datetime import datetime, timezone, timedelta
import pytz
import os.path

def read_csv_generate_events(csv_file):
    event_list = []
    with open (csv_file, 'r') as csv_content:
        csv_reader = csv.reader(csv_content, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            event = icalendar.Event()
            event.add('summary', row[0])
            event.add('description', row[5])
            tz = pytz.timezone("Asia/Shanghai")
            startDate = datetime.strptime(row[2], '%Y-%m-%d %H:%M')
            event.add('dtstart', startDate)
            endDate = datetime.strptime(row[3], '%Y-%m-%d %H:%M')
            event.add('dtend', endDate)
            event_list.append(event)
    csv_content.close()
    return event_list


def write_events(event_list, uid = "AnarL(anar930906@gmail.com)", calendarName = "节假日调休日历", description = "中国节假日调休日历"):
    cal = icalendar.Calendar()
    cal.add("name", calendarName)
    cal.add('uid', uid)
    cal.add('description', description)

    for event in event_list:
        cal.add_component(event)

    directory = os.path.dirname(__file__)
    try:
        os.mkdir(directory, mode=0o666)
    except FileExistsError:
        print("Folder already exists")
    else:
        print("Folder was created")
    
    f = open(os.path.join(directory, 'ChinaHoliday.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()

def main():
    folder = os.path.dirname(__file__)
    write_events(read_csv_generate_events(os.path.join(folder, 'iCalEvents.csv')))


if __name__ == "__main__":
    main()