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
import test
import sys
import json
import logging
import task
import schedule
import repo
import git
import gitdb
from datetime import datetime

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s: %(message)s')

###############################################################################
# Support functions
###############################################################################

#######################################
#
#######################################
def testing():
    test.testTask()
    # test.pathInTask()
    # test.addTestSchedule()
    # test.scheduleByQstn()
    # test.pathsToTestPath()
    # test.mkPathInput()
    # test.getPathInfo()
    # test.allignQstnPath()
    # test.getNewPaths()
    # test.rand1()
    # test.rand()
    # test.getQstnIds()
    # test.getPaths()
    # test.next()
    # test.scheduleTask1()
    # test.summarizeQstn()
    # test.mkTestPath()
    # test.handleQuestion()
    # test.getUnq()
    # test.handleJira()
    # test.processReq()
    # test.jiraProcess()
    # test.modStts()
    # test.jiraSearch()
    # test.nextTask()
    # test.clearRefs()
    # test.getGitHash()
    # test.validateBranchQ()
    # test.defaultSettings()
    # test.getRow()
    # test.taskTest()
    # test.fetchallQuery()
    # test.modMultiVals()
    # test.modTbl()
    # test.addTestPaths()
    # test.testMySqlConnector()
    # test.getPathsInQstn()

    # test.repoTest()
    # test.modTbl()
    # test.modMultiVals2()
    # test.modMultiVals()
    # test.qstnToTestPath()
    # test.scheduleTask()
    sys.exit()

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### testing components
    # testing()

    ### Get next task
    terminateQ = False
    while not terminateQ:
        try:
            aTask = task.next()
            if len(aTask) < 1:
                logging.info("No pending tasks: sleeping")
                time.sleep(int(os.environ.get('sleepTime')))
                continue
            ## Update status to running
            task.modStts(aTask["id"], "running",
                cols=["started"],vals=[datetime.utcnow()])

            ## Validate and checkout gitBranch and gitHash
            aTask["gitHash"] = repo.getGitHash(aTask)

        except git.exc.GitCommandError as err:
            msgErr = "Task {id} has an invalid gitBranch: {branch}".format(
                id=aTask["id"], branch=aTask["gitBranch"])
            task.modStts(aTask["id"], "fail",
                cols=["msg", "finished"],
                vals=["Invalid gitBranch", datetime.utcnow()])
            logging.error(msgErr)
        except gitdb.exc.BadName as err:
            msgErr = "Task {id} has an invalid gitHash: {gitHash}".format(
                id=aTask["id"], gitHash=aTask["gitHash"])
            task.modStts(aTask["id"], "fail",
                cols=["msg", "finished"],
                vals=["Invalid gitHash", datetime.utcnow()])
            logging.error(msgErr)
        except NameError as err:
            logging.error(err)
        except KeyboardInterrupt:
            ### Add cleanup code if needed
            terminateQ = True
        except:
            logging.error(msgErr)
        else:
            rslt = schedule.task(aTask)