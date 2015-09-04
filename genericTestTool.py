#!/usr/local/bin python3
#Author: Arko Basu
#Date  : 07212015
#Copyright: HGST Inc.
#Description: Generic Automated Tool

from toolBase import ImportXMLSampleSource
from toolBase import procSoftPack as PSP
from toolBase import dynamicMapping2 as DM2
import argparse
import sys
import os
import time
from xml.etree.ElementTree import Element, SubElement, tostring
from toolBase import utils as UTIL

def LookForDataSource():

	"""This function looks for data sources in SampleFiles folder to start the script with if no command line arguments have not been provided for compiling source"""

	filePath = os.path.join(os.path.dirname(__file__), 'workFiles','sampleFiles')
	listOfFileNames = []
	for dirpath, dirnames, filenames in os.walk(filePath):
		for files in filenames:
			if files.endswith(".xml"):
				absFileLocation = os.path.join(filePath,files)
				listOfFileNames.append(absFileLocation)
	return listOfFileNames

def ProcessXMLDataSource(xmlDataSource):

	"""This fucntion calls the method from toolsBase/main.py to process the original XML sample data source containing the software package details"""

	importedSoftPackg = ImportXMLSampleSource(xmlDataSource)
	
	return importedSoftPackg

def XMLDirectoryForSoftwarePackage(softwarePackageDirectory):

	"""This function returns the XML Script directory under the software package"""

	choiceDir = 0
	dirnames1 = os.listdir(softwarePackageDirectory)
	listOfIndex = []
	for dirname in dirnames1:
		if 'XML' not in dirname:
			listOfIndex.append(dirnames1.index(dirname))
	dirnames11 = [i for j,i in enumerate(dirnames1) if j not in listOfIndex]
	if len(dirnames11) > 1:
		print(list(enumerate(dirnames11)))
		choiceDir = int(input("There are more than one XML script directory in the software package as listed above. Enter the serial number for which one you wish to proceed with?: "))
		XMLFolder = dirnames11[choiceDir]
	else:
		XMLFolder = dirnames11[0]
	dirName = os.path.join(softwarePackageDirectory, XMLFolder)
	if not os.path.exists(dirName):
		print("Directory for software package not found. There is something wrong with the script buildup while processing the sample data source. Please start by processing the sample XML data source.")
	return dirName


#This is the starting point of the entire test framework. This is where the command line startup arguments are defined, and based on that the processing is triggerred.
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Generic Automated System test tool")
	parser.add_argument('-d','--dataSource', dest='XMLFileName', help='absolute path for the sample XML data source. If this is not provided, the System proceeds with any already compiled test source that it may find in the working directory. If it does not find that too as well, then it looks for the sampleFiles for any default schema that is stored there.')
	parser.add_argument('-cL','--createLogs', dest='logFilePath', help='absolute path for the generation of log files. If this is not provided, the System creates the log files in the /workFiles/processedFiles/"SoftwarePackageName"/LogFiles/"CurrentDateTime"')
	args = parser.parse_args()
	inputDataSource = args.XMLFileName
	logFilePath = args.logFilePath

	xmlDataSource = ''
	dictionaryOfSoftwarePackages = {}
	dictOfPackages = {}

	if inputDataSource is not None:
		xmlDataSource = inputDataSource
	else:
		print("No input XML Data source provided in command arguments discovered. Test Suit is checking the sample XML Files folder for any default schema available.")
		listOfXMLDataSource = LookForDataSource()
		if len(listOfXMLDataSource) > 0:
			print("The Sample XML Data sources found in the directory are: ")
			print(list(enumerate(listOfXMLDataSource)))
			while True:
				try:
					yesOrNo = (input("Do you wish to proceed with any of the above data sources(Y)? Or do you wish to continue into framework(N) : ")).upper()
					if yesOrNo == 'Y':
						sourceNum = int(input("Enter the serial number from the above list, of which one do you wish to proceed with? : "))
						#handle number entered for parsing source XML Script
						xmlDataSource = listOfXMLDataSource[sourceNum]
						break
					elif yesOrNo == 'N':
						print("Ok. No XML Import to be performed.")
						break
				except ValueError:
					print("Oops! That's not a number. Try Again... ")
				else:
					print("Please enter correct option again.")
		else:
			print("No sample XML data source found. This is crazy. I don't have anything to work with. Sorry. I'm done.")
			sys.exit(0)

	if xmlDataSource != '':
		importSoftPackg = ProcessXMLDataSource(xmlDataSource)
		
	softwarePackagesStoredInFolderName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'workFiles','processedFiles')
	dirname = os.listdir(softwarePackagesStoredInFolderName)

	print("Checking source directory for compiled software packages.")		
	while True:
		if len(dirname) > 0:
			num = 1
			for indvdir in dirname:
				dictOfPackages[num] = indvdir
				dictionaryOfSoftwarePackages[num] = os.path.join(softwarePackagesStoredInFolderName,indvdir)
				num = num + 1
			print("---------------------------------------------------------------------------------------------------------")
			print("Compiled software packages found in source directory: ")
			print(dictOfPackages)
			print("---------------------------------------------------------------------------------------------------------")
			print("Okay. How do you wish to proceed?")
			print("1. Add dynamic mapping for compiled software packages.")
			print("2. Automated test suit trigger for compiled software packages.")
			print("3. To exit the framework")
			option = int(input("Please chose from the above options on how you wish to proceed: "))
			if option > 3:
				print("Wrong Option selected. Try again.")
			if option == 3:
				print("Exiting framework.")
				break
			if option == 1:
				serial = int(input("Select the serial number from the above listed software package, for which you wish to perform dynamic mapping: "))
				XMLScriptsDir = XMLDirectoryForSoftwarePackage(dictionaryOfSoftwarePackages[serial])
				DM2.processSoftwarePackageXMLs(XMLScriptsDir)
			if option == 2:
				serial = int(input("Select the serial number from the above listed software package, for which you wish to run the test suit: "))
				XMLScriptsDir = XMLDirectoryForSoftwarePackage(dictionaryOfSoftwarePackages[serial])	
				PSP.processSoftwarePackage(dictOfPackages[serial],XMLScriptsDir,logFilePath)
		else:
			print("No compiled software packages were found. Please try processing a XML data source from the beginning.")
			break


