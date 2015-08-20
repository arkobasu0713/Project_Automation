#author: Arko Basu[HGST Inc]
import os
import sys
import datetime
import xml.etree.ElementTree as ETProc
from xml.etree.ElementTree import Element, SubElement, tostring
import subprocess
from . import utils as UTIL

def createOutputLogDirectory(logFilePath, XMLFolder):
	if logFilePath == '' or logFilePath is None:
		print("No log file path provided in the argument. Hence creating in the default directory location.")
		defLogLocation = os.path.join(XMLFolder,'..','LogDump')
		if os.path.exists(defLogLocation):
			print("Default Log Path already exists.")
			return defLogLocation
		else:
			os.mkdir(defLogLocation)
			return defLogLocation
	else:
		if not os.path.exists(logFilePath):
			os.mkdir(logFilePath)
			return logFilePath
		elif os.path.exists(logFilePath):
			print("Argument Location provided for generating log files already exists.")
			return logFilePath

		
class processSoftwarePackage(object):
	"""This is the function which processes the individial XMLs and runs them agains the system specific CLI and logs the output."""
	def __init__(self,softwarePackageName,softwarePackageXMLFolder,logFilePath):
		self.packageName = softwarePackageName
		self.XMLFolder = softwarePackageXMLFolder
		self.logFilePath = logFilePath
		self.files, self.dictionaryOfAbsPathForXMLs = UTIL.retreiveXMLFilesAndTheirAbsPath(self.XMLFolder)
		
		self.outputLocation = createOutputLogDirectory(self.logFilePath, self.XMLFolder)
		
		if len(self.files) > 0:
			print("Command scripts found in the directory: ")
			print(self.files)
			print("")
		while True:
			try:
				serial = int(input("Select the serial number of the command that you wish to run the test suit for, from the above list. Enter a higher serial number to exit. "))
				break
			except ValueError:
				print("This is not a valid number. Try again.")
				print(self.files)

		if serial > len(self.files) :
			print("No such command. Hence Exit.")
		else:
			comdScrpt = UTIL.procXMLScrpt(self.dictionaryOfAbsPathForXMLs[serial])
			UTIL.generateAndRunScripts(comdScrpt,self.outputLocation, self.packageName)
