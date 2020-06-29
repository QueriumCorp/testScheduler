import sys
import json

### get filter json from command line
def getFilter():
    if len(sys.argv) != 2:
        print ("Please provide json filters:")
        print ('python3 main.py \'{"summary":"OSCAGc07s01*", "labels": ["CSULAWeek01"], "fields":["key"], "qstnType":"StepWise"}\'')
        sys.exit(1)

    filter = json.loads(sys.argv[1])
    # print(json.dumps(filter, sort_keys=True, indent=4, separators=(",", ": ")))
    return filter