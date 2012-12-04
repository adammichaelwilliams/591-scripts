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
    #Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USAimport wx

import os
import re
import random
import math
import wx


class BottleAttributes:
	bottlePath = None
	libsPath = None
	statsPath = None
	datasetPath = None
	networkPath = None
	objectsReference = {}
	surrogatesIds = None
	cachesPath = None
	surrogatesCaches={}
	originsIds = None
	clientIds = None
	totalWebSiteSize = 0
	allObjectIds = []
	nRetries = None
	mean = None
	
	def reset(self):
		self.bottlePath = None
		self.libsPath = None
		self.statsPath = None
		self.datasetPath = None
		self.networkPath = None
		self.objectsReference = {}
		self.surrogatesIds = None
		self.cachesPath = None
		self.surrogatesCaches={}
		self.originsIds = None
		self.clientIds = None
		self.totalWebSiteSize = 0
		self.allObjectIds = []
		self.nRetries = None
		self.mean = None
		

bottleAttributes = BottleAttributes()

def compareRequestsByTime(req1, req2):
	pat = re.compile("[+]?(\d+(\.\d*)?|\d*\.\d+)([eE][+]?\d+)?(\ +)(\d+)")
	patRes1 = pat.match(req1)
	patRes2 = pat.match(req2)

	return int(float(patRes1.group(1))-float(patRes2.group(1)))

def processAndSaveTraffic(parent, clients, traffic):
	#open file
	try:
		fin = open(traffic, 'r')
	except:
		showSomeError(parent,"Error: While opening file: <"+traffic+">")
		return 1

	#parse file to check format
	#build a reference e.g. clientsReference[234234] = 234234
	clientsReference={}
	pat = re.compile("[+]?(\d+(\.\d*)?|\d*\.\d+)([eE][+]?\d+)?(\ +)(\d+)(\ +)[+]?(\d+(\.\d*)?|\d*\.\d+)([eE][+]?\d+)?")
	for line in fin:
		patRes = pat.match(line)
		if patRes == None:
			showSomeError(parent, "invalid traffic file format")
			return 1
		clientsReference[int(patRes.group(5))] = int(patRes.group(5))

	#check if the client the user provided and the clients in the trace file are the same in  number
	processTraffic = False
	if(len(clientsReference) != clients):
		#showSomeError(parent,"clients number mishmatch between traffic and user declared\nWill process file.")
		print "Clients in trace are diffent in number than the option.\nWill randomly re-assign clients in traffic."
		processTraffic = True
		#return 1

	#check that the ids mach the increasing number of the user supplied number of clients
	if not processTraffic:
		for i in range(0, clients):
			try:
				dummy = clientsReference[i]
			except:
				#showSomeError(parent,"clients ids mishmatch between traffic and user declared\nWill process file.")
				print "Clients in trace are diffent in number than the option.\nWill randomly re-assign clients in traffic."
				processTraffic = True
				#return 1

	distributedTraffic = {}
	for i in range(0, clients):
		distributedTraffic[i]=[]

	fin.seek(0)
	for line in fin:
		patRes = pat.match(line)
		if patRes == None:
			showSomeError(parent, "invalid traffic file format")
			return 1
		#HACK:
		if processTraffic:
			distributedTraffic[    random.randint(0, clients-1)   ] += [patRes.group(1)+' ' +patRes.group(7)+'\n']
		else:
			distributedTraffic[     clientsReference[int(patRes.group(5))]   ] += [patRes.group(1)+' ' +patRes.group(7)+'\n']

	for key in distributedTraffic.keys():
		distributedTraffic[key].sort(compareRequestsByTime)

	#dump files
	for key in distributedTraffic.keys():
		try:
			fout = open(bottleAttributes.datasetPath+'/'+str(bottleAttributes.clientIds[key]),'w')
		except:
			showSomeError(parent, "error while saving traffic for clients")
			return 1
		for line in distributedTraffic[key]:
			fout.write(line)
		fout.close()



	fin.close()
	return 0

def showSomeError(parent, error):
  print "Error: ", error
	#d= wx.MessageDialog(parent, error, "ERROR", wx.OK | wx.ICON_HAND, wx.DefaultPosition)
	#d.ShowModal() # Shows it
	#d.Destroy() # finally destroy it when finished.
  return 0

def verifyObjectsFile(parent, file):
	try:
		fin = open(file, 'r')
	except:
		showSomeError(parent,"Error: While opening file: <"+file+">")
		return 1


	patObjectsFile = re.compile("(\d+)(\ +)(\d+)")
	for line in fin:
		patRes = patObjectsFile.match(line)
		if patRes == None:
			showSomeError(parent,"Error: Invalid objects file format!")
			return 1
		bottleAttributes.objectsReference[int(patRes.group(1))] = int(patRes.group(3))
		bottleAttributes.totalWebSiteSize += int(patRes.group(3))
		bottleAttributes.allObjectIds+= [ int(patRes.group(1)) ]

	for i in range(0, len(bottleAttributes.objectsReference)):
		try:
			dummy = bottleAttributes.objectsReference[i]
		except:
			showSomeError(parent,"Error: Invalid objects file format!")
			return 1

	fin.close()
	return 0

def prepareBottle(parent,options):
	#make the bottle directory
	bottleAttributes.bottlePath = options.outputDir+'/'+options.bottleName
        if not os.system("cd \""+options.outputDir+"\"; [ -d \""+ options.bottleName+"\" ]"):
            showSomeError(parent,"A bottle with the same name already exists, remove it youself!\nBottle creation aborted")
            return 1

	if os.system('mkdir \"'+ bottleAttributes.bottlePath + '\"'):
		showSomeError(parent, "Error creating bottle directory")
		return 1
	return 0

def prepareLibs(parent, options):
	#prepare libs dir
	bottleAttributes.libsPath = bottleAttributes.bottlePath+'/libs'
	if os.system('mkdir \"'+ bottleAttributes.libsPath + '\"'):
		showSomeError(parent, "Error creating libraries directory")
		return 1

	if os.system('cp \"'+options.cdnsim2Dir+'/\"*.so \"'+options.cdnsim2Dir+'/\"*.ned \"'+ bottleAttributes.libsPath+'\"'):
		showSomeError(parent, "Error copying CDNsim libraries")
		return 1

	try:
		fin = open(options.inetDir +"/nedfiles.lst", 'r')
	except:
		showSomeError(parent,"Error: While opening file: <"+options.inetDir +"/nedfiles.lst"+">")
		return 1

	for line in fin:
		if line != "\n":
			if "\n" in line:
				line = line[:len(line)-1]

			if os.system("cd \""+options.inetDir+"\"; cp \""+line+"\" \""+bottleAttributes.libsPath+'\"'):
				showSomeError(parent,"Error: While copying INET files")
				return 1
	fin.close()
	if os.system("cd \""+options.inetDir+"\"; cp ./bin/INET \""+bottleAttributes.bottlePath+'\"'):
		showSomeError(parent,"Error: While copying INET binary")
		return 1

	if os.system("cp \""+options.omnetppDir+"/lib/\"* \""+bottleAttributes.libsPath+'\"'):
		showSomeError(parent,"Error: While copying OMNETpp libs")
		return 1

	return 0

def prepareStats(parent, options):
	#prepare stats dir
	bottleAttributes.statsPath = bottleAttributes.bottlePath+'/stats'
	if os.system('mkdir \"'+ bottleAttributes.statsPath+'\"'):
		showSomeError(parent, "Error creating statistics directory")
		return 1
	return 0

def prepareDataset(parent, options):
	bottleAttributes.datasetPath = bottleAttributes.bottlePath+'/dataset'
	if os.system('mkdir \"'+ bottleAttributes.datasetPath+'\"'):
		showSomeError(parent, "Error creating dataset directory")
		return 1

	if os.system('cp \"'+options.objects + '\" \"' +bottleAttributes.datasetPath+'/objects\"'):
		showSomeError(parent, "Error copying objects, " + 'cp '+options.objects + ' ' +bottleAttributes.datasetPath+'/objects')
		return 1

	if verifyObjectsFile(parent,bottleAttributes.datasetPath+'/objects'):
		return 1

	return processAndSaveTraffic(parent, options.clients, options.traffic)

def prepareNetwork(parent, options):
	#open file
	try:
		fin = open(options.routersGraphFile, 'r')
	except:
		showSomeError(parent,"Error: While routers file: <"+options.routersGraphFile+">")
		return 1

	routersReference = {}
	pat = re.compile("(\d+)(\ +)(\d+)")
	for line in fin:
		patRes = pat.match(line)
		if patRes == None:
			showSomeError(parent,"Error: Invalid routers file format!")
			return 1
		routersReference[int(patRes.group(1))] = []
		routersReference[int(patRes.group(3))] = []

	fin.seek(0)
	nRouters = len(routersReference)
	routerIds = range(0, nRouters)
	for i in routerIds:
		try:
			dummy = routersReference[i]
		except:
			showSomeError(parent,"Error: Invalid routers file format!")
			return 1

	for line in fin:
		patRes = pat.match(line)
		if patRes == None:
			showSomeError(parent,"Error: Invalid routers file format!")
			return 1
		routersReference[int(patRes.group(1))] += [int(patRes.group(3))]
		routersReference[int(patRes.group(3))] += [int(patRes.group(1))]

	for i in routerIds:
		try:
			set(routersReference[i])
			list(routersReference[i])
		except:
			showSomeError(parent,"Error: Invalid routers file format!")
			return 1
	fin.close()

	bottleAttributes.clientIds = range(nRouters, nRouters+options.clients)
	clientsReference = {}
	for i in bottleAttributes.clientIds:
		clientsReference[i]=random.choice(routerIds)
		routersReference[clientsReference[i]] += [i]


	bottleAttributes.surrogatesIds = range(nRouters+options.clients, nRouters+options.clients+options.surrogates)
	surrogatesReference = {}
	for i in bottleAttributes.surrogatesIds:
		surrogatesReference[i]=random.choice(routerIds)
		routersReference[surrogatesReference[i]] += [i]

	bottleAttributes.originsIds = range(nRouters+options.clients+options.surrogates, nRouters+options.clients+options.surrogates+options.origins)
	originsReference = {}
	for i in bottleAttributes.originsIds:
		originsReference[i]=random.choice(routerIds)
		routersReference[originsReference[i]] += [i]

	bottleAttributes.networkPath = bottleAttributes.bottlePath+'/network'
	if os.system('mkdir \"'+ bottleAttributes.networkPath+'\"'):
		showSomeError(parent, "Error creating network directory")
		return 1

	try:
		fout = open(bottleAttributes.networkPath+'/base.ned','w')
	except:
		showSomeError(parent, "error while saving network")
		return 1

	fout.write("""import
	"StaticContentExchange_StateTester",
	"CDN_RequestsAssignerReceiver",
	"StaticContentExchange_ServicePeer",
	"StaticContentExchange_ClientUnit",
	"StaticContentExchange_AlternateServerDetector",
	"CDN_CentralUnit",
	"Stats",
	"StaticContentExchange_ClientNegotiator",
	"StaticContentExchange_ServerUnit",
	"StaticContentExchange_ServerNegotiator",
	"Router",
	"FlatNetworkConfigurator",
	"ChannelInstaller";\n""")

	fout.write("""
	channel fiberline
		delay 0.1us;\n\t\tdatarate """)
	fout.write(str(int(options.linkSpeed)*1000000)+""";
	endchannel\n\n""")

	fout.write("""module Base
	parameters:
		//
	submodules:
		channelInstaller: ChannelInstaller;
			parameters:
				channelClass = "ThruputMeteringChannel",
				channelAttrs = "format=u";
			display: "p=98,50;i=block/cogwheel_s";
		configurator: FlatNetworkConfigurator;
			parameters:
				moduleTypes = "Router GenericHost",
				nonIPModuleTypes = "CDN_CentralUnit Stats",
				networkAddress = "145.236.0.0",
				netmask = "255.255.0.0";
			display: "p=185,50;i=block/cogwheel_s";\n\t\tcdn_CentralUnit: CDN_CentralUnit;\n\t\tstats: Stats;\n""");

	for i in routerIds:
		fout.write("\t\tr"+str(i)+""": Router;\n\t\t\tdisplay: "i=abstract/router";\n""")

	for i in bottleAttributes.clientIds:
		fout.write("\t\tc"+str(i)+""": GenericHost;\n\t\t\tdisplay: "i=device/laptop";\n""")

	for i in bottleAttributes.surrogatesIds:
		fout.write("\t\ts"+str(i)+""": GenericHost;\n\t\t\tdisplay: "i=device/server_l";\n""")

	for i in bottleAttributes.originsIds:
		fout.write("\t\to"+str(i)+""": GenericHost;\n\t\t\tdisplay: "i=device/server_s";\n""")

	fout.write("\tconnections nocheck:\n")

	try:
		foutGraph = open(bottleAttributes.networkPath+'/networkGraph','w')
	except:
		showSomeError(parent, "error while saving network")
		return 1
        
	for i in routersReference.keys():
		for k in routersReference[i]:
			if k in routerIds:
				fout.write("\t\tr"+str(i)+".out++ --> fiberline --> r"+str(k)+".in++;\n")
                                foutGraph.write("r"+str(i)+" r"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.clientIds:
				fout.write("\t\tr"+str(i)+".out++ --> fiberline --> c"+str(k)+".in++;\n")
                                foutGraph.write("r"+str(i)+" c"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.surrogatesIds:
				fout.write("\t\tr"+str(i)+".out++ --> fiberline --> s"+str(k)+".in++;\n")
                                foutGraph.write("r"+str(i)+" s"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.originsIds:
				fout.write("\t\tr"+str(i)+".out++ --> fiberline --> o"+str(k)+".in++;\n")
                                foutGraph.write("r"+str(i)+" o"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")

	for i in clientsReference.keys():
		for k in [clientsReference[i]]:
			if k in routerIds:
				fout.write("\t\tc"+str(i)+".out++ --> fiberline --> r"+str(k)+".in++;\n")
                                foutGraph.write("c"+str(i)+" r"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.clientIds:
				fout.write("\t\tc"+str(i)+".out++ --> fiberline --> c"+str(k)+".in++;\n")
                                foutGraph.write("c"+str(i)+" c"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.surrogatesIds:
				fout.write("\t\tc"+str(i)+".out++ --> fiberline --> s"+str(k)+".in++;\n")
                                foutGraph.write("c"+str(i)+" s"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.originsIds:
				fout.write("\t\tc"+str(i)+".out++ --> fiberline --> o"+str(k)+".in++;\n")
                                foutGraph.write("c"+str(i)+" o"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")

	for i in surrogatesReference.keys():
		for k in [surrogatesReference[i]]:
			if k in routerIds:
				fout.write("\t\ts"+str(i)+".out++ --> fiberline --> r"+str(k)+".in++;\n")
                                foutGraph.write("s"+str(i)+" r"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.clientIds:
				fout.write("\t\ts"+str(i)+".out++ --> fiberline --> c"+str(k)+".in++;\n")
                                foutGraph.write("s"+str(i)+" c"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.surrogatesIds:
				fout.write("\t\ts"+str(i)+".out++ --> fiberline --> s"+str(k)+".in++;\n")
                                foutGraph.write("s"+str(i)+" s"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.originsIds:
				fout.write("\t\ts"+str(i)+".out++ --> fiberline --> o"+str(k)+".in++;\n")
                                foutGraph.write("s"+str(i)+" o"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")

	for i in originsReference.keys():
		for k in [originsReference[i]]:
			if k in routerIds:
				fout.write("\t\to"+str(i)+".out++ --> fiberline --> r"+str(k)+".in++;\n")
                                foutGraph.write("o"+str(i)+" r"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.clientIds:
				fout.write("\t\to"+str(i)+".out++ --> fiberline --> c"+str(k)+".in++;\n")
                                foutGraph.write("o"+str(i)+" c"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.surrogatesIds:
				fout.write("\t\to"+str(i)+".out++ --> fiberline --> s"+str(k)+".in++;\n")
                                foutGraph.write("o"+str(i)+" s"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")
			elif k in bottleAttributes.originsIds:
				fout.write("\t\to"+str(i)+".out++ --> fiberline --> o"+str(k)+".in++;\n")
                                foutGraph.write("o"+str(i)+" o"+str(k)+" "+str(int(options.linkSpeed)*1000000)+"\n")

	fout.write("endmodule\n\n")
	fout.write("network base : Base\nendnetwork")
	fout.close()
        foutGraph.close();


def verifyCacheContentFile(parent, file, cacheSize):
	try:
		fin = open(file, 'r')
	except:
		showSomeError(parent,"Error: While opening file: <"+file+">")
		return 1

	currentSize = 0
	patObjectsFile = re.compile("(\d+)")
	for line in fin:
		patRes = patObjectsFile.match(line)
		if patRes == None:
			showSomeError(parent,"Error: Invalid objects file format!")
			return 1
		try:
			currentSize += bottleAttributes.objectsReference[int(patRes.group(1))]
		except:
			showSomeError(parent,"Error: Detected object that do not exist in reference!")
			return 1

	if currentSize > cacheSize:
		showSomeError(parent,"Error: Objects do not fit in cache!")
		return 1

	fin.close()


def prepareCaches(parent, options):
	bottleAttributes.cachesPath = bottleAttributes.bottlePath+"/caches"
	if os.system("mkdir \""+bottleAttributes.cachesPath+'\"'):
		showSomeError(parent, "Error creating caches directory")
		return 1
	try:
		fin = open(options.placement, 'r')
	except:
		showSomeError(parent,"Error: While opening file: <"+options.placement+">")
		return 1

	expectedSurrogatesRange = range(0, options.surrogates)

	patInt = re.compile("(\d+)")
	patDouble = re.compile("[+]?(\d+(\.\d*)?|\d*\.\d+)([eE][+]?\d+)?")

	while True:
		#read surrogate index
		line = fin.readline()
		if line == "":
			break


		patRes = patInt.match(line)
		if patRes == None:
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected surrogate index")
			return 1
		currentSurrogateIndex = int(patRes.group(1))

		if currentSurrogateIndex not in expectedSurrogatesRange:
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected surrogate index in the range [0 -numberOfSurrogateServer)")
			return 1

		#read number of caches
		line = fin.readline()
		if line == "":
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected number of caches")
			return 1

		patRes = patInt.match(line)
		if patRes == None:
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected number of caches")
			return 1
		numberOfCaches = int(patRes.group(1))
		if numberOfCaches != 1:
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected number of cache = 1")
			return 1

		#read file that contains objects
		line = fin.readline()
		if line == "":
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected surrogate index")
			return 1

		if '\n' in line:
			line = line[:len(line)-1]

		file = line

		#read cache type
		line = fin.readline()
		if line == "":
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected cache type")
			return 1

		if '\n' in line:
			line = line[:len(line)-1]

		cacheType = line

		#read cache size in bytes
		line = fin.readline()
		if line == "":
			return 1

		patRes = patDouble.match(line)
		if patRes == None:
			showSomeError(parent,"Error: While reading placement file, invalid file format. Excpected cache size")
			return 1
		cacheSize = float(patRes.group(1))

		expectedSurrogatesRange.remove(currentSurrogateIndex)

		if(file != "NULL"):
			#verify that the file has proper format and that it fits in cache
			if verifyCacheContentFile(parent, os.path.join(options.placementDir,file), cacheSize):
				return 1

			if os.system("cp \""+os.path.join(options.placementDir,file)+"\" \""+bottleAttributes.cachesPath+"/"+str(bottleAttributes.surrogatesIds[currentSurrogateIndex])+'\"'):
				showSomeError(parent,"Error: While copying placement file "+os.path.join(options.placementDir,file)+" to "+bottleAttributes.cachesPath+"/"+str(bottleAttributes.surrogatesIds[currentSurrogateIndex]))
				return 1
		else:
			if os.system("touch \"" + bottleAttributes.cachesPath+"/"+str(bottleAttributes.surrogatesIds[currentSurrogateIndex])+'\"'):
				showSomeError(parent,"Error: While copying placement file "+os.path.join(options.placementDir,file)+" to "+bottleAttributes.cachesPath+"/"+str(bottleAttributes.surrogatesIds[currentSurrogateIndex]))
				return 1

		bottleAttributes.surrogatesCaches[bottleAttributes.surrogatesIds[currentSurrogateIndex]] = ["./caches/"+str(bottleAttributes.surrogatesIds[currentSurrogateIndex]),cacheType, cacheSize]


	if len(expectedSurrogatesRange)!=0:
		showSomeError(parent,"Error: While reading placement file, invalid file format. Not all surrogates' caches are configured")
		return 1

	fin.close()

def prepareInis(parent, options):
	try:
		fout = open(bottleAttributes.bottlePath+'/'+"omnetpp.ini",'w')
	except:
		showSomeError(parent, "error while creating omnetpp.ini")
		return 1
	fout.write(
"""
[General]
load-libs="./libs/CDNsimlib"

include nedsToBeLoaded.ini

network = base

[Cmdenv]
express-mode = yes
module-messages = no
event-banners = no
message-trace = no
autoflush = no
performance-display = no
status-frequency= 999999999

[OutVectors]
**.enabled = no


[Tkenv]
default-run=1

[Parameters]
################################################

include surrogatesOptions.ini

include originsOptions.ini

include clientsOptions.ini

include stats.ini

include centralUnitOptions.ini

################################################

**.downloaderClass="DownloadersBase"

# tcp settings


**.tcp.mss = """)

	fout.write(str(1 * 1024))
	fout.write("\n")
	fout.write("**.tcp.advertisedWindow = ")
	fout.write(str(1*14*1024))
	fout.write("\n")
	fout.write("""
**.tcp.tcpAlgorithmClass="TCPReno"
**.tcp.recordStats=false
**.tcp.sendQueueClass="TCPMsgBasedSendQueue"
**.tcp.receiveQueueClass="TCPMsgBasedRcvQueue"

# ip settings
**.routingFile=""
**.ip.procDelay=10us
**.IPForward=false

# ARP configuration
**.arp.retryTimeout = 1
**.arp.retryCount = 3
**.arp.cacheTimeout = 100
**.networkLayer.proxyARP = true  # Host's is hardwired "false"

# NIC configuration
**.ppp[*].queueType = "DropTailQueue" # in routers
**.ppp[*].queue.frameCapacity = 10  # in routers


""")
	fout.write("\n\n**.cdn_RequestsAssignerReceiver.nRetries="+str(options.nRetries)+"\n**.cdn_RequestsAssignerReceiver.mean="+str(options.mean))
	fout.close()

	#set up surrogates

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"surrogatesOptions.ini",'w')
	except:
		showSomeError(parent, "error while creating surrogatesOptions.ini")
		return 1

	for key in bottleAttributes.surrogatesCaches.keys():
		fout.write("**.s"+str(key)+".cdn_RequestsAssignerReceiver.commandsScript = \"NULL\"\n")
		fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.cacheType = \""+bottleAttributes.surrogatesCaches[key][1]+"\"\n")
		if options.shrink is True:
			fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.shrink = 1\n")
		else:
			fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.shrink = 0\n")
		fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.cacheContents = \""+bottleAttributes.surrogatesCaches[key][0]+"\"\n")
		fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.cacheSizeInMbs = \""+str(math.ceil((( bottleAttributes.surrogatesCaches[key][2] / 1024.0 ) / 1024.0)))+"\"\n")

		fout.write("**.s"+str(key)+".staticContentExchange_ServicePeer.objectsReference = \"./dataset/objects\"\n")
		fout.write("**.s"+str(key)+".nServerHandlers = "+str(options.surrogatesIn) +"\n")

		fout.write("**.s"+str(key)+".nClientHandlers = "+str(1) +"\n")
		fout.write("**.s"+str(key)+".nDownloaders = "+str(options.surrogatesOut) +"\n")
		fout.write("**.s"+str(key)+".type = \"s\"\n")
		fout.write("\n")

	fout.close()

	#set up clients

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"clientsOptions.ini",'w')
	except:
		showSomeError(parent, "error while creating clientsOptions.ini")
		return 1

	for key in bottleAttributes.clientIds:
		fout.write("**.c"+str(key)+".cdn_RequestsAssignerReceiver.commandsScript = \"./dataset/"+str(key)+"\"\n")
		fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.cacheType = \"LRU\"\n")
		if options.shrink is True:
			fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.shrink = 1\n")
		else:
			fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.shrink = 0\n")

		fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.cacheContents = \"NULL\"\n")
		fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.cacheSizeInMbs = \"0.0\"\n")

		fout.write("**.c"+str(key)+".staticContentExchange_ServicePeer.objectsReference = \"./dataset/objects\"\n")
		fout.write("**.c"+str(key)+".nServerHandlers = 0\n")

		fout.write("**.c"+str(key)+".nClientHandlers = "+str(1) +"\n")
		fout.write("**.c"+str(key)+".nDownloaders = "+str(options.clientsOut) +"\n")
		fout.write("**.c"+str(key)+".type = \"c\"\n")

		fout.write("\n")

	fout.close()

	#set up origins
	try:
		fout = open(bottleAttributes.cachesPath+'/'+"originsContent",'w')
	except:
		showSomeError(parent, "error while creating originsOptions.ini")
		return 1

	for objId in bottleAttributes.allObjectIds:
		fout.write(str(objId)+" s\n")
		

	fout.close()

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"originsOptions.ini",'w')
	except:
		showSomeError(parent, "error while creating originsOptions.ini")
		return 1

	for key in bottleAttributes.originsIds:
		fout.write("**.o"+str(key)+".cdn_RequestsAssignerReceiver.commandsScript = \"NULL\"\n")
		fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.cacheType = \"LRU\"\n")
		if options.shrink is True:
			fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.shrink = 1\n")
		else:
			fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.shrink = 0\n")
		fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.cacheContents = \"./caches/originsContent\"\n")
		fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.cacheSizeInMbs = \""+str(math.ceil((( bottleAttributes.totalWebSiteSize / 1024.0 ) / 1024.0)))+"\"\n")

		fout.write("**.o"+str(key)+".staticContentExchange_ServicePeer.objectsReference = \"./dataset/objects\"\n")
		fout.write("**.o"+str(key)+".nServerHandlers = "+str(options.originsIn)+"\n")

		fout.write("**.o"+str(key)+".nClientHandlers = 0\n")
		fout.write("**.o"+str(key)+".nDownloaders = 0\n")
		fout.write("**.o"+str(key)+".type = \"o\"\n")
		fout.write("\n")

	fout.close()

	#set up central unit

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"centralUnitOptions.ini",'w')
	except:
		showSomeError(parent, "error while creating centralUnitOptions.ini")
		return 1

	fout.write("**.cdn_CentralUnit.policy = \""+str(options.policy)+"\"")

	fout.close()

	#set up stats

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"stats.ini",'w')
	except:
		showSomeError(parent, "error while creating stats.ini")
		return 1

	fout.write("**.stats.statsFile = \"./stats/stats\"")

	fout.close()

	#set up nedsToBeLoaded

	try:
		fout = open(bottleAttributes.bottlePath+'/'+"nedsToBeLoaded.ini",'w')
	except:
		showSomeError(parent, "error while creating nedsToBeLoaded.ini")
		return 1

	fout.write("preload-ned-files = ./network/*.ned ./libs/*.ned")

	fout.close()

def buildBottle(parent,options):
	bottleAttributes.reset()
	
	if prepareBottle(parent,options):
		showSomeError(parent,"Bottle creation aborted")
		return

	if prepareLibs(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return

	if prepareStats(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return
	random.seed(options.netSeed)
	if prepareNetwork(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return
	random.seed(options.traceSeed)
	if prepareDataset(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return

	if prepareCaches(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return

	if prepareInis(parent, options):
		showSomeError(parent,"Bottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return

	
	if not os.system("cd \""+options.outputDir+"\"; [ -f \""+ options.bottleName+".tgz\" ]"):
		showSomeError(parent,"A bottle with the same name already exists, remove it youself!\nBottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return
	
	if os.system("cd \""+options.outputDir+"\"; tar cfz \""+ options.bottleName+".tgz\" \"" +options.bottleName+"\"; rm -r \""+options.bottleName+'\"'):
		showSomeError(parent,"Failed o create archive.\nBottle creation aborted")
		os.system("rm -rf \""+bottleAttributes.bottlePath+'\"')
		return
	print "Bottle created successfully"
	#d= wx.MessageDialog(parent, "Bottle created successfully.", "All ok", wx.OK)
	#d.ShowModal() # Shows it
	#d.Destroy() # finally destroy it when finished.





