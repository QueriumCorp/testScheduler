###############################################################################
# test.py
# Testing module
###############################################################################
from mysql.connector import errorcode
import mysql.connector
import task
import repo
import json
from datetime import datetime
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

def next():
    task.modStts(71, "pending", ["msg"], [""])
    rslt = task.next()
    # rslt = schedule.task(aTask)
    print(rslt)

def template():
    rslt = "template"
    print (rslt)


if __name__ == '__main__':
    next()