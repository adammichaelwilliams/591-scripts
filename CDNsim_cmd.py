#	Use run.sh to call this file among others.
#  
# To use this file:
# python CDNsim_cmd.py {{Bottle_name}} {{Options_filename}}
#


#! /usr/bin/python

import os
import BottleBuilder
import sys
from optparse import OptionParser

class Options:
    currentPath = None
    policy = None

    routersGraphFile = None
    clients = None
    surrogates = None
    origins = None
    linkSpeed = None

    clientsOut = None
    surrogatesOut = None
    surrogatesIn = None
    originsIn = None

    traffic = None
    objects = None

    placement = None
    placementDir = None

    outputDir = None
		#Declared in CDNsim.py as cdnsimDir, but cdnsim2Dir used in BottleMaker
    cdnsim2Dir = None
    bottleName = None
    inetDir = None
    omnetppDir = None

    nRetries = None
    mean = None

    shrink = None
    netSeed = 0
    traceSeed = 0

options = Options()

# Assume input parameters are
# ......
#
def main(argv):         

	bottleName = argv[1]
	print len(argv)
	if len(argv) == 3 :
		print "Using options file"
		optionsFile = argv[2]
		f = open(optionsFile, 'r')
		for line in f:
				attrName = line.split()[0]
				attrValue = line.split()[1]
				if attrValue.isdigit():
					attrValue = int(attrValue)
				if hasattr(options, attrName):
					setattr(options, attrName, attrValue)
				else:
					print "Improper attribute name: ", attrName
					sys.exit()
	else: 
		print "No options file, using defaults"

		#Page1
			#0 - Cooperative Environment (closest surrogate)
			#1 - Non-Cooperative Environment (closest origin)
			#2 - Cooperative Environment (random surrogate)
			#3 - Cooperative Environment (surrogate load balance)
		options.policy = 0

		#Page2
		options.linkSpeed = 1000
		options.clients = 100
		options.surrogates = 1	
		options.origins = 1 
		options.clientsOut = 10	
		options.surrogatesOut = 10		
		options.surrogatesIn = 10 
		options.originsIn = 10 
		options.nRetries = 10 
		options.mean = 5 

		#page4
		options.shrink = False

	options.routersGraphFile = os.getcwd()+"/CDNsim/CDNsimdoc/sample_data/step2/as3037"
	#Page3
	options.traffic = os.getcwd()+"/591repo/InputGen/traffic.in"
	options.objects = os.getcwd()+"/591repo/InputGen/website.in"

	#page4
	options.placement = os.getcwd()+"/591repo/InputGen/placement.in"
	options.placementDir = os.getcwd()+"/591repo/InputGen"

	#page5
	options.cdnsim2Dir = os.getcwd()+"/CDNsim/CDNsimlib"
	options.inetDir = os.getcwd()+"/INET-20061020"
	options.omnetppDir = os.getcwd()+"/omnetpp-3.3p1"

	#set output directory
	print os.getcwd()
	options.outputDir = os.getcwd()+"/output/" + bottleName
	#if not os.path.exists(options.outputDir):
	#	os.mkdir(options.outputDir)
	options.bottleName = argv[1]

	BottleBuilder.buildBottle("fake", options)

main(sys.argv)
