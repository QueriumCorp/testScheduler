###############################################################################
# test.py
# Testing module
###############################################################################
import jql
from dotenv import load_dotenv
load_dotenv()

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
