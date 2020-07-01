import sys
import json

### get request json from command line
def getRequest():
    if len(sys.argv) != 2:
        print ("Please provide json filters:")
        print ('python3 main.py \'{"summary":"OSCAGc07s01*", "labels": ["CSULAWeek01"], "fields":["key"], "qstnType":"StepWise", "makeFilter": "aNewFilterName"}\'')
        print("OR")
        print ('python3 main.py \'{"jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "qstnType":"StepWise", "fields":["key"], "makeFilter": "aNewFilterName"}\'')
        print ("OR")
        print ('python3 main.py \'{"filter":"aFilterNameFromJira", "qstnType":"StepWise"}, "fields":["key"]\'')
        sys.exit(1)

    request = json.loads(sys.argv[1])
    # print(json.dumps(filter, sort_keys=True, indent=4, separators=(",", ": ")))
    return request