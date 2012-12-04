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

def printStats():
	
	data0 = numpy.genfromtxt("/CDNsim/output/nop2p_1/reqComplete.csv", delimiter=',', dtype=None)
	data1 = numpy.genfromtxt("/CDNsim/output/p2p_1_1/reqComplete.csv", delimiter=',', dtype=None)
	data2 = numpy.genfromtxt("/CDNsim/output/p2p_2_1/reqComplete.csv", delimiter=',', dtype=None)
	data3 = numpy.genfromtxt("/CDNsim/output/p2p_3_1/reqComplete.csv", delimiter=',', dtype=None)
	xAxis0 = numpy.arange(0, len(data0), 1)
	xAxis1 = numpy.arange(0, len(data1), 1)
	xAxis2 = numpy.arange(0, len(data2), 1)
	xAxis3 = numpy.arange(0, len(data3), 1)
	
	fig = pylab.figure()
	pylab.title("10% File Data Cached on Surrogate")
	pylab.plot(xAxis0, data0, color="black", linewidth=2.5, linestyle="-", label="CDN Only")
	pylab.plot(xAxis1, data1, color="blue", linewidth=2.5, linestyle="-", label="Random p2p")
	pylab.plot(xAxis2, data2, color="red", linewidth=2.5, linestyle="-", label="Tail-end p2p")
	pylab.plot(xAxis3, data3, color="green", linewidth=2.5, linestyle="-", label="Segment-based p2p")
	pylab.legend(loc='upper left')
	fig.savefig("multi_1.png")

	#print "<b>Traffic</b><br>"
	#print "<img src='graph.png' width='500px'></img>"

	#END - Extra stats



def main():
	parser = OptionParser()
	parser.add_option("-i", "--inputGen", dest="log", help="inputGen directory", default=None)
	(options, args) = parser.parse_args()

	printStats()

if __name__ == "__main__":
	main()
