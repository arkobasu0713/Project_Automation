#author: Arko Basu[HGST Inc]
import argparse
import os
import sys
import json
import datetime
import xml.etree.ElementTree as ETProc
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as MNDOM
import subprocess

def retreiveXMLFilesAndTheirAbsPath(XMLFolder):
	files = {}
	dictionaryOfAbsPathForXMLs = {}
	for dirpath, dirnames, filenames in os.walk(XMLFolder):
		index=1
		for filename in filenames:
			if filename.endswith(".xml"):
				files[index] = filename
				dictionaryOfAbsPathForXMLs[index] = os.path.join(XMLFolder,filename)
				index = index + 1

	return files, dictionaryOfAbsPathForXMLs

def parseXMLScript(commandScript):
	"""This function parses the XML Script and returns the XML tree"""		
	#Import the XML Script File
	tree = ETProc.parse(commandScript)
	if tree is not None:
		print("Import Successful.")
	else:
		print("Malicious corrupted XML File. Please generate the XML file again")
	return tree

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

		
def procXMLScrpt(FileName):
	procCommandScrpt = processCommandScript(FileName)
	print("Command name: " + str(procCommandScrpt.commandName))
	procCommandScrpt.getArguments()
	procCommandScrpt.getArgumentValues()
	procCommandScrpt.getDepMandArgs()
	procCommandScrpt.getDepOptArgs()
	procCommandScrpt.processListOfArguments()

	return procCommandScrpt

def getListOfValues(text):
	if ';' in text:
		listOfText = text.split(';')
		return listOfText
	else:
		return text

def createOutputFile(commandName,outputLocation):
	now = datetime.datetime.now()
	fileName = commandName + '_' + now.strftime("%Y%m%d_%H:%M")
	fileNamePath = os.path.join(outputLocation, fileName)
	file = open(fileNamePath, 'wt')

	return file

def writeAndRun(outputFile,commandString):
	outputFile.write(commandString)
	outputFile.write("\n")
	print(commandString)
	p = subprocess.Popen(commandString,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
	output , err = p.communicate()
	outputFile.write(str(output))
	outputFile.write("\n")
	print(str(output))

def generateAndRunScripts(comdScrpt,outputLocation, packageName):
	outputFile = createOutputFile(comdScrpt.commandName,outputLocation)
	commandString = packageName + ' ' + comdScrpt.commandName 
	writeAndRun(outputFile,commandString)	
	for elements in comdScrpt.dictionaryOfArgumentsAndTheirValues:
		modCommandString = commandString + ' ' +elements
		writeAndRun(outputFile,modCommandString)
		if isinstance(comdScrpt.dictionaryOfArgumentsAndTheirValues[elements],str):
			modCommandString1 = modCommandString + ' ' + comdScrpt.dictionaryOfArgumentsAndTheirValues[elements]
			writeAndRun(outputFile,modCommandString1)
			del modCommandString
		elif isinstance(comdScrpt.dictionaryOfArgumentsAndTheirValues[elements],list):
			for val in comdScrpt.dictionaryOfArgumentsAndTheirValues[elements]:
				modCommandString2 = modCommandString + ' ' + val
				writeAndRun(outputFile,modCommandString2)
				del modCommandString2

	outputFile.close()
		

class processCommandScript():
	def __init__(self,fileName):
		self.fileName = fileName
		self.tree = parseXMLScript(self.fileName)
		self.root = self.tree.getroot()
		self.listOfArguments = []
		self.listOfArgumentVal = []
		self.commandName = self.root.text
		self.listOfMandArg = []
		self.listOfOptArg = []
		self.dictionaryOfArgumentsAndTheirValues = {}

	def getArguments(self):
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)
		
	def getArgumentValues(self):
		for commandArgVal in self.listOfArguments:
			for val in commandArgVal.iter('parametervalues'):
				self.listOfArgumentVal.append(val)
				break
		
	def getDepMandArgs(self):
		for commandArg in self.listOfArguments:
			for val in commandArg.iter('additionalMandDependantArgument'):
				self.listOfMandArg.append(val)
		
	def getDepOptArgs(self):
		for commandArg in self.listOfArguments:
			for val in commandArg.iter('additionalOptDependantArgument'):
				self.listOfOptArg.append(val)

	def processListOfArguments(self):
		for index in range(len(self.listOfArguments)):
			commandtext = self.listOfArguments[index].text
			self.dictionaryOfArgumentsAndTheirValues[commandtext] = getListOfValues(self.listOfArgumentVal[index].text)
		
		
class processSoftwarePackage(object):
	"""This is the function which processes the individial XMLs and runs them agains the system specific CLI and logs the output."""
	def __init__(self,softwarePackageName,softwarePackageXMLFolder,logFilePath):
		self.packageName = softwarePackageName
		self.XMLFolder = softwarePackageXMLFolder
		self.logFilePath = logFilePath
		self.files, self.dictionaryOfAbsPathForXMLs = retreiveXMLFilesAndTheirAbsPath(self.XMLFolder)
		
		self.outputLocation = createOutputLogDirectory(self.logFilePath, self.XMLFolder)
		
		if len(self.files) > 0:
			print("Command scripts found in the directory: ")
			print(self.files)
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
			comdScrpt = procXMLScrpt(self.dictionaryOfAbsPathForXMLs[serial])
			generateAndRunScripts(comdScrpt,self.outputLocation, self.packageName)
