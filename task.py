###############################################################################
# task.py
# Handle tasks
###############################################################################
import dbConn

###############################################################################
# Support functions
###############################################################################

#######################################
# Make objects
#######################################
def mkObj(keys, data):
    return dict(zip(keys, data))

def mkObjs(keys, data):
    return list(map(lambda aRow: dict(zip(keys, aRow)), data))

###############################################################################
# Main logic
###############################################################################
def next():
    data = dbConn.getRow(
        "testSchedule", ["status"], ["pending"],
        dbConn.getFields("testSchedule"))

    return mkObj(dbConn.getFields("testSchedule"), data)