###############################################################################
# The module is to figure out when to schedule a test based on the reccurence
# field in the testSchedule table
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import datetime
import dbConn
import repo
import schedule
import mysql.connector
import logging
import time

###############################################################################
# Constants
###############################################################################
recByTime = ["daily", "weekly", "monthly", "yearly"]
ignoreMsg = ["Not the time"]

###############################################################################
# Support functions
###############################################################################

#######################################
# Create a test schedule based on the recurring schedule in testSchedule
#######################################
# Dup the recurring schedule to a new row
#   - Don't copy the recurrence field
#   - Make sure created date is the current time when the new row was created


#######################################
# Get recurring schedules from the testSchedule table
#######################################
def getRecurringSchedules():
    tbl = "testSchedule"
    condCols = ["status"]
    condVals = ["recurring"]
    fldsRtrn = dbConn.getFields("testSchedule")

    # Get recurring tasks
    rslt = dbConn.getRow(tbl, condCols, condVals,
                         fldsRtrn, fltr="", mkObjQ=True)

    return rslt


#######################################
# Decode rrule
#######################################
def decodeRrule(aRule):
    parts = aRule.split(";")

    obj = {}
    for aPart in parts:
        [k, v] = aPart.split("=")
        obj[k] = int(v) if k=="INTERVAL" else v

    return obj

#######################################
# Convert time to seconds
#######################################
def timeToSec(aDatetime):
    return aDatetime.hour*60*60 + aDatetime.minute*60 + aDatetime.second

#######################################
# Determine if a test should be scheduled based on recurrence time
#######################################
def timeToRunQ(rrule, createdDt, stampNow=datetime.datetime.utcnow()):
    switcher = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "yearly": 365,
    }
    # Convert the FREQ value into days
    divider = switcher.get(rrule["FREQ"].lower(), 0)

    # Factor in the interval value
    interval = 1 if "INTERVAL" not in rrule.keys() else rrule["INTERVAL"]
    divider *= interval
    if divider == 0:
        raise ValueError("Invalid FREQ value")
    dateDiff = stampNow - createdDt
    logging.debug("dateDiff: {}".format(dateDiff))
    logging.debug ("divider: {}".format(divider))

    # Determine if it's on the day since the recurring schedule created
    if dateDiff.days % divider == 0:
        timeCreated = timeToSec(createdDt)
        timeNow = timeToSec(stampNow)
        timeDiff = timeNow - timeCreated
        logging.debug("timeDiff: {}".format(timeDiff))
        runIntervalTime = int(os.environ.get('sleepTime'))
        if timeNow >= timeCreated and timeDiff < runIntervalTime:
            return True

    return False

#######################################
# Determine if the recurring schedule had already run on the given gitHash
#######################################
def mkScheduleQ(aSchedule, aHash):
    tbl = "testSchedule"
    cols = ["name", "gitBranch", "gitHash"]
    vals = [aSchedule["name"], aSchedule["gitBranch"], aHash]
    rtrn = ["id"]
    rslt = dbConn.getRow(tbl, cols, vals, rtrn, fltr="", mkObjQ=True)
    if len(rslt) < 1:
        return True

    return False

#######################################
# Jira field has paths
#######################################
def jiraGotPathsQ(aSchedule):
    if "jira" not in aSchedule:
        return False
    if "paths" not in aSchedule["jira"]:
        return False
    if len(aSchedule["jira"]["paths"]) < 1:
        return False

    return True

#######################################
# Make the jira field of a test based on a reccuring schedule
# If NEWSAMPLEON is true in rrule or it is the first test, make a new sample
# set. In this case, no work is needed and just return the jira field of
# the recurring schedule.
# In other case, the new jira field is based path IDs that were tested
# previously.
#######################################
def mkJiraField(rrule, aSchedule):

    # Case: NEWSAMPLEON is true
    if "NEWSAMPLEON" in rrule.keys() and rrule["NEWSAMPLEON"].lower() == "true":
        return aSchedule["jira"]

    # Case: The first time a test is being scheduled based on the recurring test
    allTests = dbConn.getRow(
        "testSchedule",
        ["name", "gitBranch", "mmaVersion"],
        [aSchedule["name"], aSchedule["gitBranch"], aSchedule["mmaVersion"]],
        ["id", "status", "jira"],
        fltr="ORDER BY created DESC",
        mkObjQ=True
    )
    logging.debug("All of the previous tests in {name}: {cnt}".format(
        name=aSchedule["name"], cnt=len(allTests)))
    if len(allTests) <= 1:
        return aSchedule["jira"]

    # Other cases
    # Extract the tests that have completed or scheduled
    statusCompleted = [
        "reported", "success", "failSome", "scheduled", "pending"]
    oldSchedules = list(filter(
        lambda x: x["status"] in statusCompleted, allTests))

    for anOldSchedule in oldSchedules:
        # If jira field contains path IDs, just return it
        if jiraGotPathsQ(anOldSchedule):
            return anOldSchedule["jira"]

        # If jira field does not contain path IDs, build it from testPath
        # NOTE: Very unusual case that this function go this far. If a test was
        # scheduled based on a recurring schedule, there must be a test with
        # paths in its jira field
        pathIds = dbConn.getRow(
            "testPath",
            ["schedule_id"],
            [anOldSchedule["id"]],
            ["path_id"],
            fltr=""
        )
        if len(pathIds) > 0:
            return {"paths": [i[0] for i in pathIds]}

    # When a jira field can't be built based on an old test, use
    # the jira field of the recurrence test
    # Senario: the first test of the recurring schedule will have this issue
    return aSchedule["jira"]


#######################################
# Make a s scheduled
#######################################
def mkSchedule(aSchedule, stampNow=datetime.datetime.utcnow()):
    rrule = decodeRrule(aSchedule["rrule"])
    if "FREQ" not in rrule:
        raise NameError("rrule is missing: FREQ")

    # logging.debug("created: {}".format(aSchedule["created"]))
    # logging.debug("now: {}".format(stampNow))
    # Determine if the recurrence is based on time
    if not timeToRunQ(rrule, aSchedule["created"], stampNow=stampNow):
        return {"status": False, "result": "Not the time"}

    gitHash = None
    try:
        # Get the latest gitHash on the schedule branch
        gitHash = repo.getGitHash(aSchedule)

        if mkScheduleQ(aSchedule, gitHash):
            newSchedule = schedule.defaultSettings(
                "testSchedule",
                aSchedule,
                skip=[
                    "status", "host", "pid", "gitBranch", "gitHash",
                    "msg", "rrule", "jiraResp", "started", "finished",
                    "created", "updated", "jira"
                ]
            )
            # Update the fields of the new schedule
            newSchedule["gitHash"] = gitHash
            newSchedule["status"] = "pending"
            # Build the jira field of the new schedule based a previous test
            newSchedule["jira"] = mkJiraField(rrule, aSchedule)


            # These fields are handled by the database, so remove them
            if "id" in newSchedule:
                newSchedule.pop("id")
            if "created" in newSchedule:
                newSchedule.pop("created")
            if "updated" in newSchedule:
                newSchedule.pop("updated")

            # Add the new schedule in testSchedule
            dbConn.addTestSchedule(newSchedule)
            return {"status": True, "result": "Scheduled a test based on the recurring schedule: {name}".format(
                name=aSchedule["name"]
            )}
        else:
            return {
                "status": False,
                "result": "Test {name} had already scheduled at gitHash {hash} on gitBranch {branch}".format(
                    name=aSchedule["name"], branch=aSchedule["gitBranch"],
                    hash=gitHash)
            }
    except mysql.connector.Error:
        return {
            "status": False,
            "result": "Database connection failed"
        }
    except NameError:
        return {
            "status": False,
            "result": "Invalid gitBranch: {branch}".format(
                branch=aSchedule["gitBranch"])
        }
    except Exception as err:
        return {
            "status": False,
            "result": "Invalid gitHash: {hash}".format(
                hash=aSchedule["gitHash"])
        }


###############################################################################
# Main logic
###############################################################################
def scheduleByRecurrence():
    schedules = getRecurringSchedules()
    # logging.debug(schedules)

    sleepQ = False
    currStamp = datetime.datetime.utcnow()
    for aSchedule in schedules:
        rslt = mkSchedule(aSchedule, stampNow=currStamp)

        # Don't want to log bunch of "Not the time" messages
        if "result" in rslt and rslt["result"] in ignoreMsg:
            continue

        logging.info("Processing recurrence schedule: {name}".format(
            name=aSchedule["name"]))
        logging.info("{stts} - {msg}".format(
            stts="Success" if rslt["status"] else "Fail",
            msg=rslt["result"]
        ))
        sleepQ |= rslt["status"]

    if sleepQ:
        logging.debug("Sleep after scheduling a recurring test")
        time.sleep(int(os.environ.get('sleepTime')))
