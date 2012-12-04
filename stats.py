#! /usr/bin/python
    #This file is part of CDNsim.

    #CDNsim is free software; you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation; either version 2 of the License, or
    #(at your option) any later version.

    #CDNsim is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with CDNsim; if not, write to the Free Software
    #Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import sys
from optparse import OptionParser
import re
import math
import md5
import numpy
from matplotlib import pylab
from scipy import stats
from array import *

def buildObjectsReference(objects):
	try:
		fin = open(objects, 'r')
	except:
		sys.exit("Error: While opening file <" + objects + ">")

	objectsReference = {}
	pat = re.compile("(\d+)(\ +)(\d+)")

	for line in fin:
		patRes = pat.match(line)
		if patRes == None:
			print "Error: Invalid objects file format!"
			sys.exit(2)
		objectsReference[patRes.group(1)] = int(patRes.group(3))

	fin.close()
	return objectsReference

def printStats(log, objectsReference):
	try:
		fin = open(log, 'r')
	except:
		sys.exit("Error: While opening file <" + log + ">")


	hits = 0
	byteHits =0
	misses = 0
	byteMisses =0

	completedRequests = 0
	abortedRequests = 0

	totalCompletitionTime = 0

	retries = 0
	notEnoughClientOut = 0
	failedPulls = 0
	notEnoughSurrogateOut = 0
	notEnoughSurrogateIn = 0
	notEnoughOriginIn = 0
	maxCompletionTime = 0
	minCompletionTime = 100
	completionTime = 0
	completionArray = []

	for line in fin:
		line = line[:len(line)-1]
		splittedLine = line.split(",")
		
		if "SURROGATE" in splittedLine and "HIT" in splittedLine:
			hits += 1
			byteHits += objectsReference[splittedLine[4]]
			continue

		if "SURROGATE" in splittedLine and "MISS" in splittedLine:
			misses += 1
			byteMisses += objectsReference[splittedLine[4]]
			continue

		if "COMPLETED" in splittedLine:
			completionTime = float(splittedLine[6]) - float(splittedLine[5])
			completionArray.append(completionTime)	
			if(completionTime > maxCompletionTime):
				maxCompletionTime = completionTime 
			if(completionTime < minCompletionTime):
				minCompletionTime = completionTime 
			completedRequests += 1
			totalCompletitionTime += completionTime 

		if "ABORTED" in splittedLine:
			abortedRequests  += 1
		
		if "CLIENT" in splittedLine:
			notEnoughClientOut += line.count("Client: No available downloader");
			retries += int(splittedLine[4])
			failedPulls += line.count("FAILED PULL")
			notEnoughSurrogateOut += line.count("Surrogate: No available downloader")
			notEnoughSurrogateIn += line.count("Surrogate: No available server handler")
			notEnoughOriginIn += line.count("Origin: No available server handler")


#START - Extra stats			
	completionArray = sorted(completionArray)
	xAxis = numpy.arange(0, len(completionArray), 1)
	numpy.savetxt("reqComplete.csv", completionArray, delimiter=",")
	fig = pylab.figure()
	pylab.plot(xAxis, completionArray)
	fig.savefig("graph.png")

	print "<br><img src='graph.png' width='500px' align='bottom' style='float: left; padding-bottom: 100px;' ></img></br>"

	print "99% :", stats.scoreatpercentile(completionArray, 99), "<br>"
	print "50% :", stats.scoreatpercentile(completionArray, 50), "<br>"
	print "1% :", stats.scoreatpercentile(completionArray, 1), "<br>"
	#END - Extra stats

	print "<br>"
	print "<b>CLIENT SIDE MEASUREMENTS</b><br>"
	print "Completed requests: ", completedRequests, "<br>"
	print "Aborted requests: ", abortedRequests, "<br>"
	print "Max request time: ", maxCompletionTime, "<br>"
	print "Min request time: ", minCompletionTime, "<br>"
	print "Retries: ", retries, "<br>"
	print "Not enough outgoing connections: ", notEnoughClientOut, "<br>"

	if(completedRequests > 0):
		print "\t\t","Mean response time: ",float(totalCompletitionTime) / float(completedRequests), "<br>"
	else:
		print "\t\t","Mean response time: nan", "<br>"

	print "<b>SURROGATE SIDE MEASUREMENTS</b><br>"
	if hits + misses > 0:
		print "Hit ratio percentage: ", (float(hits) / (float(hits) + float(misses))) * 100, "<br>"
		print "Byte hit ratio percentage: ", (float(byteHits) / (float(byteHits) + float(byteMisses))) * 100, "<br>"

	else:
		print "Hit ratio percentage: nan", "<br>"
		print "Byte hit ratio percentage: nan", "<br>"
	print "Not enough outgoing connections: ", notEnoughSurrogateOut, "<br>"
	print "Not enough incoming connections: ", notEnoughSurrogateIn, "<br>"
	print "Failed pulls: ", failedPulls, "<br>"

	print "<b>ORIGIN SIDE MEASUREMENTS</b><br>"
	print "Not enough incoming connections: ", notEnoughOriginIn, "<br>"

	fin.close();

def main():
	parser = OptionParser()
	parser.add_option("-l", "--log", dest="log", help="CDNsim log file", default=None)
	parser.add_option("-o", "--objects", dest="objects", help="objects reference file", default=None)
	(options, args) = parser.parse_args()
	if options.log == None or options.objects == None :
		sys.exit("Error: Not all options are set! Use -h, for help")
	if len(args) != 0:
		sys.exit("Error: Unwanted arguments detected! Use -h, for help")

	printStats(options.log, buildObjectsReference(options.objects))

if __name__ == "__main__":
	main()
