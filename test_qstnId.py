###############################################################################
# Testing module
# python3 test_qstnId.py
###############################################################################
import dbConn
from schedule import processReq, task as scheduleTask, pathsToTestPath
from schedule import handleQuestionId, qstnIdsToTestPath
from schedule import mkPathInput


def getTask(idSchedule=1976):
    tbl = "testSchedule"
    data = dbConn.getRow(
        tbl, ["id"], [idSchedule],
        dbConn.getFields("testSchedule"), mkObjQ=True)

    return data[0]


def test_handleQuestionId():
    aTask = getTask()

    rslt = handleQuestionId(aTask)
    print(rslt)


def test_processReq():
    aTask = getTask()

    rslt = processReq(aTask)
    print(rslt)


def test_qstnIdsToTestPath():
    qstnIdsToTestPath({})


def test_scheduleTask():
    aTask = getTask()

    scheduleTask(aTask)


def test_pathsToTestPath():
    aTask = getTask()
    aQstnId = 89963
    aTask["question_id"] = aQstnId

    pathsToTestPath(aTask)


def test_mkPathInput():
    aTask = getTask()
    aQstnId = 89963
    aTask["question_id"] = aQstnId

    rslt = mkPathInput(aTask)
    print(rslt)


def test_run():
    # testScheduleId = 2063
    # testScheduleId = 2064
    testScheduleId = 2065

    aTask = getTask(testScheduleId)
    scheduleTask(aTask)


if __name__ == '__main__':
    test_run()
    # test_mkPathInput()
    # test_processReq()
    # test_handleQuestionId()