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

def printStats(log):
	try:
		fin = open(log+"/traffic.stats", 'r')
	except:
		sys.exit("Error: While opening file <" + log + ">")
	
	cdnData = []
	p2pData = []

	count = 0
	for line in fin:
		line = line[:len(line)-1]
		splittedLine = line.split("\t")
		cdnData.append(int(splittedLine[1]))
		p2pData.append(int(splittedLine[2]))

#START - Extra stats			
	xAxis = numpy.arange(0, len(cdnData), 1)
	fig = pylab.figure()
	pylab.plot(xAxis, cdnData, color="blue", linewidth=2.5, linestyle="-", label="CDN supplied data")
	pylab.plot(xAxis, p2pData)
	pylab.plot(xAxis, p2pData, color="red", linewidth=2.5, linestyle="-", label="p2p supplied data")
	pylab.legend(loc='center left')
	fig.savefig("traffic.png")

	#print "<b>Traffic</b><br>"
	#print "<img src='graph.png' width='500px'></img>"

	#END - Extra stats

	print "<br>"

	fin.close();

def main():
	parser = OptionParser()
	parser.add_option("-i", "--inputGen", dest="log", help="inputGen directory", default=None)
	(options, args) = parser.parse_args()
	if options.log == None :
		sys.exit("Error: Not all options are set! Use -h, for help")
	if len(args) != 0:
		sys.exit("Error: Unwanted arguments detected! Use -h, for help")

	printStats(options.log)

if __name__ == "__main__":
	main()
