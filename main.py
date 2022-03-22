###############################################################################
# main.py
# The main module
#
# Get started documentation
# https://github.com/QueriumCorp/testScheduler/wiki/Get-Started
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import time
import jql
import test
import sys
import json
import logging
import task
import schedule
import repo
import recurrence
import git
import gitdb
from datetime import datetime

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s: %(message)s')

###############################################################################
# Support functions
###############################################################################

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### Get next task
    terminateQ = False
    while not terminateQ:
        # Schedule any recurring tests
        recurrence.scheduleByRecurrence()

        try:
            aTask = task.next()
            if len(aTask) < 1:
                logging.debug("No pending tasks: sleeping")
                time.sleep(int(os.environ.get('sleepTime')))
                continue
            ## Update status to running
            task.modStts(aTask["id"], "scheduling",
                cols=["started"],vals=[datetime.utcnow()])

            ## Validate and checkout gitBranch and gitHash
            aTask["gitHash"] = repo.getGitHash(aTask)

        except git.exc.RepositoryDirtyError as err:
            msgErr = "The {dir} has uncommitted changes".format(
                dir=repo.getRepoDir())
            task.modStts(aTask["id"], "fail",
                cols=["msg", "finished"],
                vals=[msgErr, datetime.utcnow()])
            logging.error(msgErr)
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
            schedule.task(aTask)