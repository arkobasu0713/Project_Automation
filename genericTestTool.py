#!/usr/local/bin python3
#Author: Arko Basu
#Date  : 07212015
#Copyright: HGST Inc.
#Description: Generic Automated Tool

from toolBase import ImportXMLSampleSource, CreateWorkFiles
import argparse
import sys
import os
import time

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Generic Automated System test tool")
	parser.add_argument('-d','--dataSource', dest='XMLFileName', help='absolute path for the sample XML data source. If this is not provided, the System looks for XML sample source in its deafult workFiles directory to find the available already imported sources.')
	parser.add_argument('-cL','--createLogs', dest='LogFilePath', help='absolute path for the generation of log files. If this is not provided, the System creates the log files in the /workFiles/processedFiles/"SoftwarePackageName"/LogFiles')
	args = parser.parse_args()
	xmlDataSource = args.XMLFileName
	LogFilePath = args.LogFilePath
	softwarePackagesStoredInFolderName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'workFiles','processedFiles')
	dirname = os.listdir(softwarePackagesStoredInFolderName)
	
	dictionaryOfSoftwarePackages = {}
	if xmlDataSource is None:
		print("Going into source software package directory.")		
		#Go to workFiles/CompiledXMLSources

		num = 1

		if len(dirname) > 0:
			print("Compiled sources for the following software packages are found: ")			
			for indvdir in dirname:
				dictionaryOfSoftwarePackages[num] = indvdir
				print(str(num) + ". " + indvdir)
				num = num + 1
		else:
			print("No compiled sources discovered. Please load any of the software packages using -d option on the command line to go ahead with the import")
		
	else:
		File = ImportXMLSampleSource(xmlDataSource)
		print("Software Package detected in sample XML Source: " + File.root.tag)
		softwarePackageFolder = CreateWorkFiles(File.root)
		print("At this point, the input data source has been processed and the correspoding files have been generated in " + softwarePackageFolder.dirName)
		print("Please verify the XML files in the above mentioned folder.")


	#At this point the individual XML files with the commands and their parameters are created in the working directory

	selectionOfSoftwarePackage = input("Please input the serial number for the software package that you wish to run the test suit for: ")





	
