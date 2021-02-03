###############################################################################
# test.py
# Testing module
###############################################################################
import jql
import input
import jiraFilter
import util
from dotenv import load_dotenv
load_dotenv()
import os
from urllib.parse import urlencode
import dbConn
import schedule
from datetime import datetime
import json
import repo
import task
# import MySQLdb
import mysql.connector
from mysql.connector import errorcode

def modTbl():
    tbl = "testSchedule"
    colsCond = ["id"]
    valsCond = [1]
    # col = "skipStatuses"
    # val = '["invalid"]'
    col = "status"
    val = 'pending'

    dbConn.modTbl(tbl, colsCond, valsCond, col, val)

def addTestPaths():
    data = [{"name": "test", "author": "eb"}]
    dbConn.addTestPaths(data)

def getPathsInQstn():
    rslt = dbConn.getPathsInQstn("QUES-12889", [], ["id", "status"])
    # rslt = dbConn.getPathsInQstn(58418, [], ["id", "status"])
    print("getPathsInQstn:", rslt)


def testMySqlConnector():
    # query = ("SELECT id FROM question WHERE unq=%s")
    query = ("SELECT id FROM question WHERE unq=%s")
    value = ("QUES-12889",)
    rslt = ""
    try:
        cnx = mysql.connector.connect(user='webappuser', password='CU9%&yBd^knWX^UL', host='67.205.165.116',database='udb')
        with cnx.cursor() as cursor:
            cursor.execute(query, value)
            rslt = cursor.fetchone()
            # print("fetchone-rslt:", rslt)
        print("rslt:", rslt)

    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    finally:
      cnx.close()





def taskTest():
    aTask = task.next()
    print(f"before: {aTask}")
    if len(aTask)>0:
        if aTask["gitHash"].lower()=="latest" and "gitBranch" in aTask:
            aTask["gitHash"] = repo.getGitHash(aTask["gitBranch"])
    print(f"after: {aTask}")

def repoTest():
    # repo.getGitHash("dev")
    # gitHash = repo.getGitHash("eb-dev")
    gitHash = repo.getGitHash("jiraApp")
    print (f"git hash: {gitHash}")

def modMultiVals2():
    data = [{'status': True, 'result': 0, 'unq': 'QUES-12889'}, {'status': True, 'result': 0, 'unq': 'QUES-12888'}, {'status': True, 'result': 0, 'unq': 'QUES-12887'}, {'status': True, 'result': 0, 'unq': 'QUES-12886'}, {'status': True, 'result': 21, 'unq': 'QUES-12885'}, {'status': True, 'result': 14, 'unq': 'QUES-12884'}, {'status': True, 'result': 12, 'unq': 'QUES-12883'}, {'status': True, 'result': 18, 'unq': 'QUES-12882'}, {'status': True, 'result': 32, 'unq': 'QUES-12881'}, {'status': True, 'result': 25, 'unq': 'QUES-12880'}, {'status': False, 'result': 'QUES-12879 was not found in UDB', 'unq': 'QUES-12879'}, {'status': True, 'result': 52, 'unq': 'QUES-12878'}, {'status': True, 'result': 47, 'unq': 'QUES-12877'}, {'status': True, 'result': 43, 'unq': 'QUES-12876'}, {'status': True, 'result': 35, 'unq': 'QUES-12875'}, {'status': True, 'result': 41, 'unq': 'QUES-12874'}, {'status': True, 'result': 45, 'unq': 'QUES-12873'}, {'status': True, 'result': 41, 'unq': 'QUES-12872'}, {'status': False, 'result': 'QUES-12871 was not found in UDB', 'unq': 'QUES-12871'}, {'status': False, 'result': 'QUES-12870 was not found in UDB', 'unq': 'QUES-12870'}, {'status': True, 'result': 21, 'unq': 'QUES-12869'}, {'status': True, 'result': 24, 'unq': 'QUES-12868'}, {'status': True, 'result': 19, 'unq': 'QUES-12867'}, {'status': True, 'result': 30, 'unq': 'QUES-12866'}, {'status': True, 'result': 25, 'unq': 'QUES-12865'}, {'status': True, 'result': 28, 'unq': 'QUES-12864'}, {'status': True, 'result': 22, 'unq': 'QUES-12863'}, {'status': True, 'result': 23, 'unq': 'QUES-12862'}, {'status': True, 'result': 16, 'unq': 'QUES-12861'}, {'status': True, 'result': 20, 'unq': 'QUES-12860'}, {'status': True, 'result': 39, 'unq': 'QUES-12819'}, {'status': True, 'result': 48, 'unq': 'QUES-12818'}, {'status': True, 'result': 43, 'unq': 'QUES-12817'}, {'status': True, 'result': 55, 'unq': 'QUES-12816'}, {'status': True, 'result': 32, 'unq': 'QUES-12815'}, {'status': True, 'result': 32, 'unq': 'QUES-12814'}, {'status': True, 'result': 40, 'unq': 'QUES-12813'}, {'status': True, 'result': 45, 'unq': 'QUES-12812'}, {'status': True, 'result': 48, 'unq': 'QUES-12811'}, {'status': True, 'result': 38, 'unq': 'QUES-12810'}, {'status': True, 'result': 25, 'unq': 'QUES-12809'}, {'status': True, 'result': 23, 'unq': 'QUES-12808'}, {'status': True, 'result': 26, 'unq': 'QUES-12807'}, {'status': True, 'result': 23, 'unq': 'QUES-12806'}, {'status': True, 'result': 22, 'unq': 'QUES-12805'}, {'status': True, 'result': 32, 'unq': 'QUES-12804'}, {'status': True, 'result': 21, 'unq': 'QUES-12803'}, {'status': True, 'result': 35, 'unq': 'QUES-12802'}, {'status': True, 'result': 25, 'unq': 'QUES-12801'}, {'status': True, 'result': 28, 'unq': 'QUES-12800'}, {'status': True, 'result': 58, 'unq': 'QUES-12052'}, {'status': True, 'result': 22, 'unq': 'QUES-12051'}, {'status': True, 'result': 95, 'unq': 'QUES-12050'}, {'status': True, 'result': 73, 'unq': 'QUES-12049'}, {'status': True, 'result': 67, 'unq': 'QUES-12048'}, {'status': True, 'result': 88, 'unq': 'QUES-12047'}, {'status': True, 'result': 81, 'unq': 'QUES-12046'}, {'status': True, 'result': 28, 'unq': 'QUES-12045'}, {'status': True, 'result': 74, 'unq': 'QUES-12044'}, {'status': True, 'result': 93, 'unq': 'QUES-12043'}, {'status': True, 'result': 72, 'unq': 'QUES-12042'}, {'status': True, 'result': 56, 'unq': 'QUES-12041'}, {'status': True, 'result': 56, 'unq': 'QUES-12040'}, {'status': True, 'result': 67, 'unq': 'QUES-12039'}, {'status': True, 'result': 58, 'unq': 'QUES-12038'}, {'status': True, 'result': 62, 'unq': 'QUES-12037'}, {'status': True, 'result': 66, 'unq': 'QUES-12036'}, {'status': True, 'result': 20, 'unq': 'QUES-12035'}, {'status': True, 'result': 59, 'unq': 'QUES-12034'}, {'status': True, 'result': 15, 'unq': 'QUES-12033'}, {'status': True, 'result': 311, 'unq': 'QUES-6019'}, {'status': True, 'result': 297, 'unq': 'QUES-6011'}]
    failedQstns = list(filter(lambda x: x["status"]==False, data))
    tbl = "testSchedule"
    colsCond = ["id"]
    valsCond = [1]
    col = ["status", "started", "msg"]
    val = [
        "Success" if len(failedQstns)==0 else "FailedSome",
        datetime.now(),
        json.dumps(data, separators=(',', ':'))
    ]

    dbConn.modMultiVals(tbl, colsCond, valsCond, col, val)


def modMultiVals():
    tbl = "testSchedule"
    colsCond = ["id"]
    valsCond = [1]
    col = ["status","msg"]
    val = ["pending","hi"]

    dbConn.modMultiVals(tbl, colsCond, valsCond, col, val)


def qstnToTestPath():
    info = {'key': 'QUES-12879'}
    settings = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'skipStatuses': '["invalid"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}

    tmp = schedule.qstnToTestPath(info, settings)
    print (tmp)

def rmExistingPaths():
    keysCond = ['name', 'path_id']
    data = [
        {"name":"5731520200708080941", "path_id":61637, "question_id":58418},
        {"name":"5731520200708080941", "path_id":62193, "question_id":58418},
        {"name":"5731520200708080941", "path_id":62739, "question_id":58418},
        {"name":"5731520200708080941", "path_id":63285, "question_id":58418},
        {"name":"5731520200708080941", "path_id":70247, "question_id":58418},
    ]
    # data = [
    #     {"name":"5731520200708080941", "path_id":1, "question_id":2}
    # ]

    tmp = schedule.rmExistingPaths(keysCond, data)
    print("none-existing", tmp)

def scheduleTask():
    print ("schedule - task")
    # data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'skipStatuses': '["invalid"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"makeFilter": "filterTest4", "qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'skipStatuses': '["invalid"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    # data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"useFilter": "filterTest1", "fields":["key"]}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'skipStatuses': '["invalid"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    schedule.task(data)

def getRow():
    print ("test - getRow")
    tmp = dbConn.getRow("testSchedule", ["id"], [1], ["id", "author"])
    # tmp = dbConn.getRow("question", ["unq"], ["QUES-12879"], ["id"])
    print (tmp)

def mkFilter():
    print ("test - mkFilter")
    name = "filterTest8"
    jql = "project = QUES AND Labels = CSULAWeek01"
    # jql = "project = QUES ANDdsf Labels = CSULAWeek01"
    # settings = {"description": "testing"}
    # settings = {"shareGroup": "AI Engineer"}
    settings = {"shareGroup": "xxx"}
    rslt = jiraFilter.mkFilter(name, jql, settings)
    # rslt = jiraFilter.mkFilter(name, jql)
    print (rslt)

def filterExistsQ():
    print ("test - filterExistsQ")
    # name = "Bug Priority Search by LO"
    # name = "Bug Priority"
    # name = "MacDemoQUES"
    # name = "utest bug collector"
    name = "Fall19bus"
    rslt = jiraFilter.filterExistsQ(name)
    print (rslt)

def nextUrl():
    print ("test - nextUrl")
    name = "QUES search"
    route, _ = jql.buildJql("filterNameSearch", name)
    urlRoot = os.environ.get('companyUrl')+route
    print("urlRoot:", urlRoot)
    urlNext = urlRoot+"&"+urlencode({"startAt": 50})
    print("urlNext:", urlNext)
    urlNext = urlRoot+"&"+urlencode({"startAt": 100})
    print("urlNext:", urlNext)

def nextPage():
    print ("test - nextPage")
    tmpResp = {
        "isLast": True,
        "startAt": 0,
        "maxResults": 50,
        "total": 500
    }
    print (util.nextPage(tmpResp))
    tmpResp = {
        "isLast": False,
        "startAt": 0,
        "maxResults": 50,
        "total": 500
    }
    print (util.nextPage(tmpResp))
    tmpResp = {
        "startAt": 0,
        "maxResults": 50,
        "total": 500
    }
    print (util.nextPage(tmpResp))
    tmpResp = {
        "startAt": 450,
        "maxResults": 50,
        "total": 500
    }
    print (util.nextPage(tmpResp))
    tmpResp = {
        "maxResults": 50,
        "total": 500
    }
    print (util.nextPage(tmpResp))
    tmpResp = {
        "maxResults": 50
    }
    print (util.nextPage(tmpResp))

def makeFilter():
    print ("test - makeFilter")
    tmpName = "QUES search"
    tmpJql = 'project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND "Mathematica Specification" !~ MatchSpec'
    jiraFilter.mkFilter(tmpName, tmpJql)

def issueSearch():
    print ("issueSearch")

    ## issueSearch
    tmpData = {
        "summary": "OSCAGc07s01*",
        # "labels": ["CSULAWeek01"],
        "fields": [
            "key", "Question Type", "MD5 Spec Hash",
            "UDB Update", "Math Class", "ID Number",
            "Mathematica Specification", "LaTeX", "QSH1", "QSH2", "QSH3",
            "Question Launch", "Source", "question stimumus",
            "description", "StepWise label", "Querium product ID",
            "EdX Specification"
        ],
        # "fields": ["key", "Question Type", "MD5 Spec Hash"],
        # "fields": ["key"],
        "qstnType": "StepWise"
    }
    tmp = jql.issueSearch(tmpData, flatten=True)
    jql.printJson(tmp)
    print("total len: ", len(tmp))

def combContents():
    ## combContents
    tmp = {
        "content": [
            {
                "content": [
                    {
                        "text": "Solve  by any method.  (\\begin{array}{c}",
                        "type": "text"
                    },
                    {
                        "type": "hardBreak"
                    },
                    {
                        "text": "6x-8y=-0.6 ",
                        "type": "text"
                    }
                ],
                "type": "paragraph"
            },
            {
                "content": [
                    {
                        "text": "3x+2y=0.9",
                        "type": "text"
                    },
                    {
                        "type": "hardBreak"
                    },
                    {
                        "text": "\\end{array})",
                        "type": "text"
                    }
                ],
                "type": "paragraph"
            }
        ]
    }
    rslt = jql.combContents(tmp)
    print(rslt)

def getFieldValue():
    ##getFieldValueV2
    tmpField = "MD5 Spec Hash"
    # tmpField = "Question Type"
    tmp = jql.getFieldValue(tmpField,
        {
            'expand': 'operations,versionedRepresentations,editmeta,changelog,renderedFields',
            'id': '47356',
            'self': 'https://querium.atlassian.net/rest/api/3/issue/47356',
            'key': 'QUES-12889',
            'fields': {
                'customfield_11300': '569b8f88d5a3e3021ea4ead6b243b91a',
                'customfield_11706': {
                    'self': 'https://querium.atlassian.net/rest/api/3/customFieldOption/10704',
                    'value': 'StepWise',
                    'id': '10704'
                }
            }
        })
    print (tmp)

def getFields():
    ## getFields
    flds = ["a", "c"]
    arr = [{"a": "one", "b": "two", "c":"three"}, {"a": "four", "b": "five"}]
    print (jql.getFields(flds, arr))

def fieldToCust():
    ## fieldToCust
    tmpField = "ID Number"
    print(tmpField, ":", jql.fieldToCust(tmpField))
    tmpField = "Querium product ID"
    print(tmpField, ":", jql.fieldToCust(tmpField))
    tmpField = "rand"
    print(tmpField, ":", jql.fieldToCust(tmpField))
    tmp = [jql.fieldToCust(i) for i in ["key", "Question Type", "MD5 Spec Hash"]]
    print(tmp)

def buildJql():
    ## test: buildJql
    tmpData = {
        "summary": "OSCAGc07s01*",
        "labels": ["CSULAWeek01"],
        "qstnType": "StepWise",
        "filds": ["key", "summary", "labels", "Question Type"]
    }
    print (jql.buildJql("issueSearch", tmpData))
    print (jql.buildJql("xxx", {"a": "one", "b": "two"}))

def getQuestion():
    ## get a jira question
    tmp = jql.getQuestion({"issue": "QUES-6019"})
    jql.printJson(tmp)

def envVar():
    ## testing environment variables
    print (os.environ.get('USER'))
    print (os.environ.get('api-token'))
