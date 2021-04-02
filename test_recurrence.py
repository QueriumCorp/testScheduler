###############################################################################
# Testing module
# To run
# python3 test_recurrence.py
###############################################################################
import logging
import recurrence
import repo
import json
import datetime
import dbConn
import schedule
from urllib.parse import urlencode
import os
import sys
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def template():
    rslt = "template"
    print(rslt)


def decodeRrule():
    # data = "FREQ=DAILY;"
    data = "TZID=US-Eastern:19970902T090000;FREQ=WEEKLY;COUNT=10"
    rslt = recurrence.decodeRrule(data)
    print(rslt)

def timeToSec():
    # data = datetime.datetime(2007, 12, 6, 16, 29, 43)
    # data = datetime.datetime(2007, 12, 6, 0, 1, 0)
    data = datetime.datetime(2007, 12, 6, 1, 0, 0)
    rslt = recurrence.timeToSec(data)
    print (rslt)

def timeToRunQ():
    aSchedule = dbConn.getRow(
        "testSchedule",
        ["id"], [18],
        dbConn.getFields("testSchedule"),
        fltr="",
        mkObjQ=True
    )[0]
    rule = recurrence.decodeRrule(aSchedule["rrule"])
    rslt = recurrence.timeToRunQ(rule, aSchedule["created"])
    print(rslt) # True

def mkScheduleQ():
    # data = {
    #     "name": "5731520200708080941",
    #     "rrule": "FREQ=DAILY",
    #     "created": datetime.datetime(2021, 3, 30, 15, 00, 00),
    #     "gitBranch": "dev",
    #     "gitHash": "latest"
    # }
    # dataHash = "22d8516d1cce5829df504e734f2abead6be061c5"
    data = {
        "name": "5731520200708080941",
        "rrule": "FREQ=DAILY",
        "created": datetime.datetime(2021, 3, 30, 15, 00, 00),
        "gitBranch": "dev",
        "gitHash": "57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3"
    }
    dataHash = "57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3"
    rslt = recurrence.mkScheduleQ(data, dataHash)
    print(rslt)

def testSchedule():
    rslt = schedule.defaultSettings(
        "testSchedule",
        {"name": "someName"},
        skip=["name"]
    )
    print (rslt)

def mkSchedule():
    tbl = "testSchedule"
    aSchedule = dbConn.getRow(tbl, ["id"], [1], dbConn.getFields(tbl), mkObjQ=True)[0]
    # print(aSchedule)
    # sys.exit()
    # START HERE
    # aSchedule["rrule"] = "FREQ=DAILY"
    aSchedule["created"] = datetime.datetime(2021, 3, 30, 15, 00, 00)
    # aSchedule["gitBranch"] = "lates"
    # aSchedule["gitHash"] = "lates"
    aSchedule["status"] = "recurring"
    aSchedule["msg"] = "someRandomMsg"

    # stampNow = datetime.datetime(2021, 3, 31, 11, 25, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 35, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 25, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 30, 00)
    stampNow = datetime.datetime(2021, 3, 31, 15, 00, 00) # True
    # stampNow = datetime.datetime(2021, 3, 31, 15, 10, 00) # False
    rslt = recurrence.mkSchedule(aSchedule, stampNow)
    print(rslt)

def scheduleByRecurrence():
    # recSchedule = schedule.defaultSettings(
    #     "testSchedule",
    #     {
    #         "name": "testRec",
    #         "status": "recurring",
    #         "rrule": "FREQ=DAILY",
    #         "created": datetime.datetime(2021, 3, 31, 9, 45, 00)
    #     }
    # )
    # dbConn.addTestSchedule(recSchedule)

    # dbConn.modField("testSchedule", "id", 18,
    #     "rrule", "FREQ=MONTHLY")
    # dbConn.modField("testSchedule", "id", 18,
    #     # "created", datetime.datetime(2021, 3, 25, 14, 46, 00))
    #     "created", datetime.datetime(2021, 3, 2, 14, 46, 00))
    recurrence.scheduleByRecurrence()

if __name__ == '__main__':
    scheduleByRecurrence()
    # mkSchedule()
    # testSchedule()
    # mkScheduleQ()
    # timeToRunQ()
    # timeToSec()
    # decodeRrule()
