###############################################################################
# Testing module
# To run
# python3 test_recurrence.py
###############################################################################
import logging
import json
import dbConn
import handleKilling
from urllib.parse import urlencode
import os
import sys
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

def processKilling():
    aTask = {"id": 102}
    handleKilling.processKilling(aTask)

def softly():
    handleKilling.softly()

if __name__ == '__main__':
    softly()
    # processKilling()
