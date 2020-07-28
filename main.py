###############################################################################
# main.py
# The main module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install requests

# To run
# python3 main.py '{"summary":"OSCAGc07s01*", "labels": ["CSULAWeek01"], "qstnType":"StepWise", "fields":["key"]}'
# or
# python3 main.py '{"jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "fields":["key"]}'
# or
# python3 main.py '{"makeFilter": "aNewFilterName", "jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "fields":["key"]}'
# or
# python3 main.py '{"useFilter": "filterTest1", "fields":["key"]}'
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import time
import input
import jql
import jiraFilter
import test
import sys
import json
import logging
import task
import schedule

logging.basicConfig(level=logging.DEBUG)

###############################################################################
# Support functions
###############################################################################

#######################################
#
#######################################

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### testing code
    test.modTbl()
    test.modMultiVals()
    # test.qstnToTestPath()
    # test.getRow()
    # test.scheduleTask()
    # test.rmExistingPaths()
    sys.exit()

    ### Get next task
    terminateQ = False
    while not terminateQ:
        try:
            task = task.next()
            if len(task)>0:
                schedule.task(task)
            else:
                logging.info("No pending tasks: sleeping")
                time.sleep(int(os.environ.get('sleepTime')))
        except KeyboardInterrupt:
            ### Add cleanup code if needed
            terminateQ = True