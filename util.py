#! /usr/bin/python
import os
import sys
from optparse import OptionParser
import math

def main():
     parser = OptionParser()
     parser.add_option("-s", "--source", default=None, help="The cdnsim stdout")
     parser.add_option("-i", "--nodeid", default=None, help="the node id")


     (options, args) = parser.parse_args()
     if options.source == None or options.nodeid == None:
          sys.exit("Error: Not all options are set! Try -h")
     if len(args) != 0:
          sys.exit("Error: Unwanted arguments detected!")
          
     try:
          fin = open(options.source,'r')
     except:
          sys.exit("Cannot open file: " + options.source)

     surrogates = {}
     clients = {}
     origins = {}
     
     for line in fin:
          line = line[:len(line)-1]

          if not "UTIL_DOWN" in line and not "UTIL_UP" in line:
               continue

          splittedLine = line.split(' ')

          if "UTIL_DOWN" in splittedLine:
               isUp = False
          else:
               isUp = True

          isClient = False
          isSurrogate = False
          isOrigin = False

          if "c" in line:
               isClient = True
          if "s" in line:
               isSurrogate = True
          if "o" in line:
               isOrigin = True

          nodeId = splittedLine[2]
          time = float(splittedLine[1])
          bytes = float(splittedLine[3])

          if isSurrogate:
               currentDictionary = surrogates
          if isClient:
               currentDictionary = clients
          if isOrigin:
               currentDictionary = origins
          
          if not currentDictionary.has_key(nodeId):
               currentDictionary[nodeId] = [0, 1, 1, 1] #n up, down, cum_util

          cum_util = currentDictionary[nodeId][3]
          n = currentDictionary[nodeId][0]
          
          if isUp is True:
               upload = bytes
               download = currentDictionary[nodeId][2]
          else:
               upload = currentDictionary[nodeId][1]
               download = bytes

	  currentDictionary[nodeId] = [n+1, upload, download, (2/math.pi) * math.atan((float(upload)) / (float(download)) )]
	  #currentDictionary[nodeId] = [n+1, upload, download, ((float(upload)) / (float(download)) )]

               

     fin.close()
     
     print "<b>SURROGATE SERVERS UTILITIES</b><br>"
     cumulativeUtility = 0.0
     nSurrogates = 0
     for key in surrogates.keys():
          cumulativeUtility = cumulativeUtility + (surrogates[key][3])
	  nSurrogates = nSurrogates + 1

     print 'Active surrogate servers: ' + str(nSurrogates) + '<br>\n'
     print 'Mean surrogate servers utility ' + str(float(cumulativeUtility)/float(nSurrogates)) + '<br>\n'
     
     #print "<b>CLIENTS UTILITIES</b><br>"
     #for key in clients.keys():
          #print key + ' '+str(clients[key][3])+'<br>\n'
     #print "<b>ORGIN SERVERS UTILITIES</b><br>"
     #for key in origins.keys():
          #print key + ' '+str(origins[key][3])+'<br>\n'
   
if __name__ == "__main__":
     main()



                    