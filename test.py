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
import datetime

def modTbl():
    tbl = "testSchedule"
    colsCond = ["id"]
    valsCond = [1]
    col = "status"
    val = "running"

    dbConn.modTbl(tbl, colsCond, valsCond, col, val)

def modMultiVals():
    tbl = "testSchedule"
    colsCond = ["id"]
    valsCond = [1]
    col = ["status","msg"]
    val = ["pending","hi"]

    dbConn.modMultiVals(tbl, colsCond, valsCond, col, val)


def qstnToTestPath():
    info = {'key': 'QUES-12879'}
    settings = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'validStatus': '["followTestingM","testing","development","followTesting","live","approved","aiTesting","jsonToPath"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}

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
    # data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'validStatus': '["invalid"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"fields":["key"],"makeFilter": "filterTest4", "qstnType":"StepWise","jql":"project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \\"Mathematica Specification\\" !~ MatchSpec"}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'validStatus': '["followTestingM","testing","development","followTesting","live","approved","aiTesting","jsonToPath"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    # data = {'id': 1, 'name': '5731520200708080941', 'jira': '{"useFilter": "filterTest1", "fields":["key"]}', 'author': 'evan', 'gradeStyle': 'gradeBasicAlgebra', 'policies': '$A1$', 'validStatus': '["followTestingM","testing","development","followTesting","live","approved","aiTesting","jsonToPath"]', 'status': 'pending', 'limitPaths': -1, 'limitStepTime': 1800, 'limitSteps': -1, 'limitPathTime': 3600, 'host': '0.0.0.0', 'pid': -1, 'gitBranch': 'dev', 'gitHash': 'latest', 'mmaVersion': '11.1', 'timeOutTime': 60, 'ruleMatchTimeOutTime': 120, 'msg': '', 'jiraResp': None, 'started': datetime.datetime(1970, 1, 1, 1, 0), 'finished': datetime.datetime(1970, 1, 1, 1, 0), 'created': datetime.datetime(2020, 7, 8, 13, 9, 48)}
    schedule.task(data)

def getRow():
    print ("test - getRow")
    # tmp = dbConn.getRow("testSchedule", ["id"], [1], ["*"])
    tmp = dbConn.getRow("question", ["unq"], ["QUES-12879"], ["id"])
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
