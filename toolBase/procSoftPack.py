#author: Arko Basu[HGST Inc]
import os
import sys
import datetime
import xml.etree.ElementTree as ETProc
from xml.etree.ElementTree import Element, SubElement, tostring
import subprocess
from . import utils as UTIL

def createOutputLogDirectory(logFilePath, XMLFolder):

	"""This method creates the Output Log Directory.
	Returns the path to the output log directory."""

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

def createTempFileDirectory(XMLFolder):

	"""This method creates the temp file directory in the compiled software package directory where the scripts are generated.
	Returns the tempfile directory path."""

	defTempLocation = os.path.join(XMLFolder,'..','TempFiles')
	if os.path.exists(defTempLocation):
		print("Default temp location already exists.")
		return defTempLocation
	else:
		os.mkdir(defTempLocation)
		print("Temp folder created at: " + defTempLocation)
		return defTempLocation

		
class processSoftwarePackage(object):

	"""This is the function which processes the individial XMLs and runs them agains the system specific CLI and logs the output."""

	def __init__(self,softwarePackageName,softwarePackageXMLFolder,logFilePath):
		self.packageName = softwarePackageName
		self.XMLFolder = softwarePackageXMLFolder
		self.logFilePath = logFilePath
		self.files, self.dictionaryOfAbsPathForXMLs = UTIL.retreiveXMLFilesAndTheirAbsPath(self.XMLFolder)
		
		self.outputLocation = createOutputLogDirectory(self.logFilePath, self.XMLFolder)
		self.tempLocation = createTempFileDirectory(self.XMLFolder)
		
		if len(self.files) > 0:
			print("Command scripts found in the directory: ")
			print(self.files)
			print("")
		while True:
			try:
				serial = [int(i) for i in (input("Select the serial number of the command that you wish to run the test suit for, from the above list. You can chose multiple serials by passing them using a semicolon(;):  ").split(';'))]
			except ValueError:
				print("This is not a valid number. Try again.")
				print(self.files)
			else:
				indexSerial = 0
				for serl in serial:
					if serl > len(self.files) or serl < 1:
						print("No such command serial " + str(serl) + ". Deleting Selection.")
						del serial[indexSerial]
					indexSerial = indexSerial + 1
				break		




		for ser in serial:
			print("Running Script: " + self.files[ser])
			listOfArgObjects = UTIL.procXMLScrpt1(self.dictionaryOfAbsPathForXMLs[ser],self.outputLocation,self.tempLocation)
			
				
