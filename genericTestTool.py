#!/usr/local/bin python3
#Author: Arko Basu
#Date  : 07212015
#Copyright: HGST Inc.
#Description: Generic Automated Tool

from toolBase import ImportXMLSampleSource, CreateWorkFiles
from toolBase import procSoftPack as PSP
import argparse
import sys
import os
import time
from xml.etree.ElementTree import Element, SubElement, tostring

def ProcessXMLDataSource(xmlDataSource):
	File = ImportXMLSampleSource(xmlDataSource)
	print("Software Package detected in sample XML Source: " + File.root.tag)
	softwarePackageFolder = CreateWorkFiles(File.root)
	print("At this point, the input data source has been processed and the correspoding files have been generated in " + softwarePackageFolder.dirName)
	print("Please verify the XML files in the above mentioned folder.")
	return File


def LookForDataSource():
	filePath = os.path.join(os.path.dirname(__file__), 'workFiles','sampleFiles')
	listOfFileNames = []
	for dirpath, dirnames, filenames in os.walk(filePath):
		for files in filenames:
			if files.endswith(".xml"):
				absFileLocation = os.path.join(filePath,files)
				listOfFileNames.append(absFileLocation)
	return listOfFileNames

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Generic Automated System test tool")
	parser.add_argument('-d','--dataSource', dest='XMLFileName', help='absolute path for the sample XML data source. If this is not provided, the System proceeds with any already compiled test source that it may find in the working directory. If it does not find that too as well, then it looks for the sampleFiles for any default schema that is stored there.')
	parser.add_argument('-cL','--createLogs', dest='LogFilePath', help='absolute path for the generation of log files. If this is not provided, the System creates the log files in the /workFiles/processedFiles/"SoftwarePackageName"/LogFiles/"CurrentDateTime"')
	args = parser.parse_args()
	xmlDataSource = args.XMLFileName
	LogFilePath = args.LogFilePath
	softwarePackagesStoredInFolderName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'workFiles','processedFiles')
	dirname = os.listdir(softwarePackagesStoredInFolderName)
	rootFileElement = None
	dictionaryOfSoftwarePackages = {}
	if xmlDataSource is None:
		print("Going into compiled software package directory.")		
		#Go to workFiles/CompiledXMLSources

		num = 1

		if len(dirname) > 0:
			print("Compiled sources for the following software packages are found: ")			
			for indvdir in dirname:
				pathForPackage = os.path.join(softwarePackagesStoredInFolderName,indvdir)
				dictionaryOfSoftwarePackages[num] = pathForPackage
				print(str(num) + ". " + indvdir)
				num = num + 1
		else:
			print("No compiled sources discovered. Test Suit is checking the sampleFiles folder for any default schema available.")
			ListOfXMLDataSource = LookForDataSource()
			indexSource = 1
			if len(ListOfXMLDataSource) > 0:
				print("The Sample XML Data sources found in the directory are: ")
				for dataSource in ListOfXMLDataSource:
					print(str(indexSource) + ". " + dataSource)
					indexSource = indexSource + 1
				yesOrNo = input("Do you wish to proceed with any of the above data sources? (Y/N) : ")
				if yesOrNo.upper() == 'Y':
					sourceNum = input("Enter the serial number from the above list, of which one do you wish to proceed with? : ")
					print("The sample data source being used for processing is: " + ListOfXMLDataSource[int(sourceNum)-1])
					xmlDataSource = ListOfXMLDataSource[int(sourceNum)-1]
					rootFileElement = ProcessXMLDataSource(xmlDataSource)
				else:
					print("I'm done. I don't know what you want me to do. Fix up your mind first.")
				
			else:
				print("No sample XML data source found. This is crazy. I don't have anything to work with. Sorry. I'm done.")
				sys.exit(0)
		
	else:
		rootFileElement = ProcessXMLDataSource(xmlDataSource)

	#Proceed with the software package processing XMLs
	selectionOfSoftwarePackage = int(input("Please input the serial number for the software package that you wish to run the test suit for: "))
	PSP.processSoftwarePackage(dictionaryOfSoftwarePackages[selectionOfSoftwarePackage],LogFilePath,rootFileElement)
	








