###############################################################################
# test.py
# Testing module
###############################################################################
from mysql.connector import errorcode
import mysql.connector
import task
import repo
import json
import datetime
import schedule
import dbConn
from urllib.parse import urlencode
import os
import jql
import input
import jira
import util
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.DEBUG)


def template():
    rslt = "template"
    print (rslt)


def pathsInSchedule():
    scheduleId = 4
    rslt = dbConn.pathsInSchedule(scheduleId)
    print("rslt:")
    print(rslt)

def addTestSchedule():
    data = {'name': '5731520200708080941', 'jira': '', 'author': 'maria@querium.com', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'skipStatuses': ['invalid'], 'status': 'testing', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': '22d8516d1cce5829df504e734f2abead6be061c5', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': '', 'started': '1970-01-01 01:00:00', 'finished': '1970-01-01 01:00:00', 'rrule': 'FREQ=DAILY', 'created': datetime.datetime(2021, 3, 30, 15, 0)}

    dbConn.addTestSchedule(data)


if __name__ == '__main__':
    addTestSchedule()
    # pathsInSchedule()