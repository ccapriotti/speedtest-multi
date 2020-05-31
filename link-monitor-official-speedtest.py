#!/usr/bin/env python3
#
# logs speedtest results
#

import time
import json
import sys
import subprocess
import datetime
from multiprocessing.pool import Pool

serverPool = ["12743", "23969", "3188", "6251", "24815", "24389", "28164"]
startTime = time.time()
exportFile = "speedtest-official-v1.log"
fullyQualifiedServers = []
results_dict = {}
SPEEDTEST = "/usr/bin/speedtest --progress=no "

def shell_run(command, runShell = True):
    out1, err1  = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=runShell).communicate()
    
    if len(err1) > 0:
        errorLevel =  255
    else:
        errorLevel = 0

    return {"errorLevel" : errorLevel, "successOutput" : out1, "errorOutput": err1 }
        
readResults = {}

for oneServer in serverPool:
    readResults[oneServer] = {}
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H:%M:%S")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        print("Server code: {}, {}".format(oneServer, timestamp) )
       
    finalCommand = SPEEDTEST + " --server-id=" + oneServer
    
    resSpeedtest = shell_run(finalCommand)
    
    if resSpeedtest["errorLevel"] == 0:
        outLine = resSpeedtest["successOutput"].decode("utf-8")
        
        for line in outLine.split("\n"):
            captureDet = [ {"download": {"startStr": "Download:", "endStr": "Mbps"}}, 
                           {"upload": {"startStr": "Upload:", "endStr": "Mbps"}},
                           {"server": {"startStr": "Server:", "endStr": "("}},
                           {"ping": {"startStr": "Latency:", "endStr": "ms"}},
                           {"result": {"startStr": "Result URL:", "endStr": ""}}
                        ]
            readResults[oneServer].update({"timestamp" : timestamp})        
            for item in captureDet:
                itemKey = list(item.keys())[0]
                startArgument = item[itemKey]["startStr"]
                endArgument = item[itemKey]["endStr"]
                lenStartArgument = len(startArgument)
                lenEndArgument = len(endArgument)
                returnResult = ""
                
                try:
                    startPos = line.index( startArgument ) + lenStartArgument
                    endPos   = line.index( endArgument )

                    if lenEndArgument > 0:
                        returnResult = line[startPos:endPos].strip()
                    else:
                        returnResult = line[startPos:].strip()

                    readResults[oneServer].update({itemKey : returnResult})

                except:
                    pass

    else:
        readResults[oneServer] = {"status":"errorReading"}         
            

maxDl = 0
maxUp = 0
minPing = 10000
outputRecord = []
runTotals = False
for item in readResults:
    if  (not "status" in readResults[item]) : 
        runTotals = True
        curDl = float(readResults[item]["download"])
        curUp = float(readResults[item]["upload"])
        curPing = float(readResults[item]["upload"])
        maxDl = (curDl if curDl > maxDl else maxDl)
        maxUp = (curUp if curUp > maxUp else maxUp)
        minPing = (curPing if curPing < minPing else minPing)
        outputRecord.append([readResults[item]["timestamp"], 
                            readResults[item]["download"],
                            readResults[item]["upload"],
                            readResults[item]["ping"],
                            readResults[item]["server"],
                            readResults[item]["result"]
                            ])
if runTotals:                            
    outputRecord.append([now.strftime("%Y-%m-%d-%H:%M:%S"),
                        str(maxDl),
                        str(maxUp),
                        str(minPing),
                        "Best values",
                        ""]
                        )    
    

if len(sys.argv) > 1:
    if sys.argv[1] == "--debug":
        for item in outputRecord:
            print(",".join(item))
    else:
        print("Unknown option")
else: 
    try:
        f = open( exportFile, "a" )
    except:
        print( "link-monitor: error opening file", exportFile )
        sys.exit( 255 )
    for item in outputRecord:
        f.write( ",".join(item) + "\n" )
    f.close()
