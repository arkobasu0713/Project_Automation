#author: Arko Basu[HGST Inc]
import os
import sys
import datetime
import xml.etree.ElementTree as ETProc
import subprocess
import ntpath
import itertools


def retreiveXMLFilesAndTheirAbsPath(XMLFolder):

	"""This function walks through the Original XML Scripts folder and returns two dictionaries of files and 
	their absolute path corresponding to serial numbers as keys for the programs to refer to.
	Returns a couple of lists containing the file names and dictionary of absolute path of the filenames found in that directory"""

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

def verifyProcessedFilesDir():

	"""This function verifies the existance of the ProcessedFiles directory in the source tree. If doesn't exist, it creates the directory"""

	procFileDir = os.path.join(os.path.dirname(__file__),'..','workFiles','processedFiles')
	if not os.path.exists(procFileDir):
		print("Processed Files directory missing. Hence creating directory for storing software packages.")		
		os.mkdir(procFileDir)
	else:
		print("Processed Files directory found.")

def verifySoftwarePackageRPMDir():
	
	"""This function verifies the existance of the directory used for storing software package's RPM files in within the source tree. If doesn't exist, it creates the directory."""

	softPackRPMDir = os.path.join(os.path.dirname(__file__),'..','workFiles','softwarePackageRPMs')
	if not os.path.exists(softPackRPMDir):
		print("Directory for RPM files of software packages not found. Hence creating directory. " + softPackRPMDir)
		os.mkdir(softPackRPMDir)
	else:
		print("Directory for storing RPM files of software packages found.")

def extractRPM(installationPackageURL):
	
	"""This function extracts the RPM file for the software package from a remote repository and stores inside RPM software package directory for later use."""
	print("Extracting file: " + installationPackageURL)

def CreateDirectoryForSoftwarePackage(softwarePackageName):

	"""This function creates a folder for software package imported through data source in workFiles/processedFiles. 
	If the folder already exists, it creates a separate folder for XML scripts with data time apended.
	Returns the dirName and the XML scripts directory."""

	dirName = os.path.join(os.path.dirname(__file__), '..', 'workFiles', 'processedFiles',softwarePackageName)
	XMLScriptDirectory = ''
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Directory for software package, " + softwarePackageName + " created at " + dirName)
		XMLScriptDirectory = os.path.join(dirName,'OriginalXMLScripts')
		os.mkdir(XMLScriptDirectory)
		print("Directory for XML scripts for corresponding software package, generated at: " + XMLScriptDirectory)
	else:
		opt = (input("Directory for software package already exists. Please note that should you wish to proceed all the previously mapped scripts will be deleted and recreated. Do you wish to continue with existing directory?(y/n):  ")).upper()
		if opt == 'Y':
			XMLScriptDirectory = os.path.join(dirName,'OriginalXMLScripts')
		else:
			XMLScriptDirectory = os.path.join(dirName,'OriginalXMLScripts'+ datetime.datetime.now().strftime("%Y%m%d_%H:%M"))
			os.mkdir(XMLScriptDirectory)
			print("Directory for XML scripts for corresponding software package, generated at: " + XMLScriptDirectory)
	return dirName, XMLScriptDirectory


def GenerateScriptForCommandNameInSoftwarePackageFolder(XMLScriptDirectory,commandName):

	"""This function creates an XML file for an individual command processed in the originating master XML Data Source.
	Returns the file object for the created xml script file."""

	fileName = commandName + ".xml"
	filePath = os.path.join(XMLScriptDirectory,fileName)
	file = open(filePath, 'wb')
	print("File " + filePath +" for command, " + commandName +" created")
	return file

def parseXMLScript(commandScript):

	"""This function parses the XML Script and returns the XML tree.
	Returns the tree of the parsed XML source script."""

	#Import the XML Script File
	tree = ETProc.parse(commandScript)
	if tree is None:
		print("Import UnSuccessful.")
	return tree

def printList(listOfArg):

	"""This function simply prints the text of the XML elements inside the list with serial numbers."""

	index = 0
	for i in listOfArg:
		text = i.text
		print(str(index) + ". " + text)
		index = index +1

def printArgsBasedOnIndex(listOfCommandArg, listOfIndex):

	"This function prints the text for the XML commandArgs and also if it has any dependency in its attribute appened with a serial number at the beginning."""

	for val in listOfIndex:
		printString = str(val) + ". " + str(listOfCommandArg[val].text)

		for commandVal in listOfCommandArg[val].findall('importsFrom'):
			printString = printString + " Has imports tag from command: " + commandVal.text + "."
			break
		for commandVal in listOfCommandArg[val].iter('parametervalues'):
			if commandVal.text not in ['None', 'NA']:
				printString = printString + " Takes in values: " + commandVal.text
			else:
				break

		for commandDep in listOfCommandArg[val].iter('additionalMandDependantArgument'):
			printString = printString + " Has mandatory dependant argument elements."
			break
		for commandDep in listOfCommandArg[val].iter('additionalOptDependantArgument'):
			printString = printString + " Has optional dependant argument elements."
			break
		print(printString)
		

def printBehaviourMappingTechnique():

	"""This is a simple print method."""

	print("Please note the heirarchy of the behaviour mapping. Start with the lowest order of mapping.")

def printDynamicMappingTechnique():
	
	"This also a simple text print message that are called from multiple places."""

	print("Please note that if a command takes mutiple arguments as dependant parameters. Pass them with semicolons(;) to generate similar test scripts.")

def getListOfValues(text):

	"""This method processes the string in the command script containing the parameter values.
	Returns a list/string of parameter values."""

	if ';' in text:
		listOfText = text.split(';')
	#TODO:need to handle range
		return listOfText
	else:
		return text

def createOutputFile(commandName,outputLocation):
	
	"""This method creates the output file based on the command name found inside the script that is being processed and time stamps it at the output location as passed.
	Returns the file object of the output file."""

	now = datetime.datetime.now()
	fileName = commandName + '_' + now.strftime("%Y%m%d_%H%M")+".txt"
	fileNamePath = os.path.join(outputLocation, fileName)
	file = open(fileNamePath, 'wt')

	return file

def RunScript(commandString):

	"""Runs a command string.
	Returns the object of Popen once the command is run."""

	p = subprocess.Popen(commandString,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
	return p

def runImportScript(commandScript,packageName):

	"""Runs the commandScript.
	Returns the object of POPEN after the run."""

	procImpScript = processCommandScriptMod(commandScript)
	commandString = procImpScript.packageName + ' ' + procImpScript.commandName
	p = RunScript(commandString)
	return p

def createTempFile(commandName,tempLocation):

	"""Creates the tempfiles in the directory of tempLocation where the scripts are to be generated with the script name as that
	of the command for which the script is being run. Date and Timestamps are appended to them.
	Returns the tempFile Object and the fileNamePath."""

	now = datetime.datetime.now()
	fileName = commandName + '_' + now.strftime("%Y%m%d_%H%M")+".txt"
	fileNamePath = os.path.join(tempLocation, fileName)
	tempFile = open(fileNamePath, 'wt')

	return tempFile, fileNamePath
	
def extractData(paramText,output):
	
	"""Extracts the data from the output file object based on the param text passed.
	Returns the listOfData extracted."""
	
	listOfData = []
	for line in output.split(os.linesep):
		if paramText.upper() in line.upper():
			param = (line.split('='))[1].strip()
			listOfData.append(param)
	return list(set(listOfData))

def findPackageName(absolutePathOfCommandScript):
	
	"""Finds the package name of the software package in which the command script resides.
	Returns the package Name."""

	head, tail = ntpath.split(absolutePathOfCommandScript)
	head1, tail1 = ntpath.split(head)
	head2, tail2 = ntpath.split(head1)
	

	return tail2

def runTempScripts(outputFileObj,tempFile):

	"Run each of the scripts found in the temp script and writes them in the output file object."""

	f = open(tempFile,'r')
	for eachLine in f:
		outputFileObj.write("Running: " + eachLine)
		outputFileObj.write('\n\n')
		p = RunScript(eachLine)
		output, err = p.communicate()
		if output.decode('ascii') == '':
			outputFileObj.write(err.decode('ascii'))
		else:
			outputFileObj.write(output.decode('ascii'))
		outputFileObj.write("\n")
	

class processCommandScriptMod():
	#This class to process the command script
	def __init__(self,fileName):
		self.fileName = fileName
		self.packageName = findPackageName(self.fileName)
		self.tree = parseXMLScript(self.fileName)
		self.root = self.tree.getroot()
		self.commandName = self.root.text
		self.listOfArguments = []
		self.dictOfParameter = {}
		self.listOfParameters = []
		self.dictionaryOfMandParameters = {}
		self.dictionaryOfOptParameters ={}
		self.listOfOutputStrings = []
		self.tempFile = None
		self.tempFileNamePath = None
		
	def getArguments(self):
	#This method gets the list of argument elements in the xml and the text in within those elements
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)
			self.listOfParameters.append(commandArg.text)

	def getArgumentsDet(self):
	#This method processes each of the command arguments found in the script and generates the parameter values and also looks for dependant arguments
		for commandArg in self.listOfArguments:
			parameter = processElement(commandArg)
			parameter.getParamValue()
			parameter.hasMandOpt()
			parameter.hasImports()
			self.dictOfParameter[parameter.parameter] = parameter.paramValues
			if parameter.hasMand == 'Y':
				self.dictionaryOfMandParameters[parameter.parameter] = parameter.listOfMandParameters
			if parameter.hasOpt == 'Y':
				self.dictionaryOfOptParameters[parameter.parameter] = parameter.listOfOptParameters
	

	def generateCommandsAndWriteToScripts(self):
	#This sub-method processes the command script details and generates the temp files which contains all scripts that are generated from the source XML
		commandString = self.packageName + ' ' + self.commandName
		for parameter in self.listOfParameters:
			commandStringWithParam = commandString + ' ' + parameter
			parameterVal = ''
			parameterMandArgs = ''
			parameterOptArgs = ''
			if parameter in self.dictionaryOfMandParameters:
				parameterMandArgs = self.dictionaryOfMandParameters[parameter]
			if parameter in self.dictionaryOfOptParameters:
				parameterOptArgs = self.dictionaryOfOptParameters[parameter]
			procParam = processParameter(parameter, parameterMandArgs, parameterOptArgs,self.dictOfParameter)
			procParam.paramVal()
			procParam.mandArg()
			procParam.optArg()
			procParam.processPrintString()
			for eachString in procParam.listOfPrintStrings:
				self.tempFile.write(commandString + ' ' + eachString)
				self.tempFile.write('\n')
		self.tempFile.close()		

class processParameter():
	#This class is for processing the parameter inside the XML scripts
	def __init__(self,parameter,mandArgs,optArgs,dictOfParameter):
		self.parameter = parameter
		self.mandArgs = mandArgs
		self.optArgs = optArgs
		self.dictOfParameter = dictOfParameter
		self.listOfParamValueStrings = []
		self.listOfMandStrings = []
		self.listOfOptStrings = []
		self.listOfPrintStrings = []

	def paramVal(self):
	#This method finds the command argument values
		if isinstance(self.dictOfParameter[self.parameter],str):
			self.listOfParamValueStrings.append(self.parameter + ' ' + self.dictOfParameter[self.parameter])
		else:
			for eachParamVal in self.dictOfParameter[self.parameter]:
				self.listOfParamValueStrings.append(self.parameter + ' ' + eachParamVal)
#		print("Param Value strings: " )
#		print(self.listOfParamValueStrings)

	def mandArg(self):
	#This method processes all the mandatory arguments and pushes them on to a list and creates all combinations of possible strings
		for eachMandArg in self.mandArgs:
			if isinstance(eachMandArg,str):
				if isinstance(self.dictOfParameter[eachMandArg],str):
					self.listOfMandStrings.append(eachMandArg + ' ' + self.dictOfParameter[eachMandArg])
				else:
					for eachMandVal in self.dictOfParameter[eachMandArg]:
						self.listOfMandStrings.append(eachMandArg + ' ' + eachMandVal)
			else:
				listOfStringsMaj = []
				for i in range(len(eachMandArg)):
					listOfStrings = []
					if isinstance(self.dictOfParameter[eachMandArg[i]],str):
						listOfStrings.append(eachMandArg[i] + ' ' + self.dictOfParameter[eachMandArg[i]])
					else:
						for eachMandVal in self.dictOfParameter[eachMandArg[i]]:
							listOfStrings.append(eachMandArg[i] + ' ' + eachMandVal)
					listOfStringsMaj.append(listOfStrings)
				for eachComb in list(itertools.product(*listOfStringsMaj)):
					string = ''
					for eachCombPart in eachComb:
						string = string + eachCombPart + ' ' 
					self.listOfMandStrings.append(string)
					
#		print("ListOfMandStrings:")
#		print(self.listOfMandStrings)	

	def optArg(self):
	#This method processes all the optional arguments and pushes them on to a list and creates all combinations of possible strings
		for eachOptArg in self.optArgs:
			if isinstance(eachOptArg,str):
				if isinstance(self.dictOfParameter[eachOptArg],str):
					self.listOfOptStrings.append(eachOptArg + ' ' + self.dictOfParameter[eachOptArg])
				else:
					for eachOptVal in self.dictOfParameter[eachOptArg]:
						self.listOfOptStrings.append(eachOptArg + ' ' + eachOptVal)
			else:
				listOfStringsMaj = []
				for i in range(len(eachOptArg)):
					listOfStrings = []
					if isinstance(self.dictOfParameter[eachOptArg[i]],str):
						listOfStrings.append(eachOptArg[i] + ' ' + self.dictOfParameter[eachOptArg[i]])
					else:
						for eachOptVal in self.dictOfParameter[eachOptArg[i]]:
							listOfStrings.append(eachOptArg[i] + ' ' + eachOptVal)
					listOfStringsMaj.append(listOfStrings)
				for eachComb in list(itertools.product(*listOfStringsMaj)):
					string = ''
					for eachCombPart in eachComb:
						string = string + eachCombPart + ' ' 
					self.listOfOptStrings.append(string)
					
#		print("ListOfOptStrings:")
#		print(self.listOfOptStrings)	

	def processPrintString(self):
	#This method creates all the possible combinations of command strings found for tha parameter along with their parameter values, extracted data from import scripts, mandatory arguments and optional arguments.
		masterList = []
		masterList.append(self.listOfParamValueStrings)
		if self.listOfMandStrings != []:
			self.listOfMandStrings.append(' ')
			masterList.append(self.listOfMandStrings)
		else:
			masterList.append([' '])
		if self.listOfOptStrings != []:
			self.listOfOptStrings.append(' ')
			masterList.append(self.listOfOptStrings)
		else:
			masterList.append([' '])
				
		for eachString in list(itertools.product(*masterList)):
			string = '' 
			for eachPartString in eachString:
				string = string + ' ' + eachPartString
			string = (string.rstrip()).lstrip()
			self.listOfPrintStrings.append(string)

		self.listOfPrintStrings.sort()

class processElement():
	#This class is for processing an element found in the XML Script
	def __init__(self,element):
		self.elem = element
		self.parameter = self.elem.text
		self.numOfChildren = len(self.elem)
		self.hasMand = 'N'
		self.hasOpt = 'N'
		self.hasImportsFrom = 'N'
		self.mandIndex = None
		self.optIndex = None
		self.importsFromIndex = None
		self.paramValues = ''
		self.listOfMandParameters = []
		self.listOfOptParameters = []
		
	def hasMandOpt(self):
	#This process is to look for any child elements of mandatory/optional arguments in within the processed element.
	#On finding such a child element, the data is extracted and pushed into a list
		for childNum in range(self.numOfChildren):
			if self.elem[childNum].tag == 'additionalMandDependantArgument':
				self.hasMand = 'Y'
				self.mandIndex = childNum
			elif self.elem[childNum].tag == 'additionalOptDependantArgument':
				self.hasOpt = 'Y'
				self.optIndex = childNum
			else:
				continue
		if self.hasMand == 'Y':
			for eachMandArgument in self.elem[self.mandIndex].findall('command'):
				if ';' in eachMandArgument.text:
					self.listOfMandParameters.append((eachMandArgument.text).split(';'))
				else:
					self.listOfMandParameters.append(eachMandArgument.text)
				
		if self.hasOpt == 'Y':
			for eachOptArgument in self.elem[self.optIndex].findall('command'):
				if ';' in eachOptArgument.text:
					self.listOfOptParameters.append((eachOptArgument.text).split(';'))
				else:
					self.listOfOptParameters.append(eachOptArgument.text)
				

	def hasImports(self):
	#This method is for finding if the element contains any import script. In case it does, that script is run and the data is extracted from the output to be passed on as the parameter values
		for childNum in range(self.numOfChildren):
			if self.elem[childNum].tag == 'importsFrom':
				self.hasImportsFrom = 'Y'
				self.importsFromIndex = childNum
		if self.hasImportsFrom == 'Y':
			packName = findPackageName(self.elem[self.importsFromIndex].text)
			p = runImportScript(self.elem[self.importsFromIndex].text,packName)
			output, err = p.communicate()
			if output.decode('ascii') == '':
				print('Import Command for ' + self.parameter + "Had a Run Error as followed: " + err.decode('ascii'))
			else:
				self.paramValues = extractData(self.parameter.strip('-'),output.decode('ascii'))


	def getParamValue(self):
	#This method is for processing the element and extracting their parameter values if there is any.
		for paramValue in self.elem.findall('parametervalues'):
			if paramValue.text not in ['None','NA']:
				self.paramValues = getListOfValues(paramValue.text)
				break

		

def procXMLScrpt1(commandScript,outputLocation,tempLocation):

	#This function has multiple method calls which processes the command script and generate temp script files with all executable commands and also runs them against the system and generates output logs

	procCommandScrpt = processCommandScriptMod(commandScript)
	procCommandScrpt.getArguments()
	procCommandScrpt.getArgumentsDet()
	procCommandScrpt.tempFile, procCommandScrpt.tempFileNamePath = createTempFile(procCommandScrpt.commandName, tempLocation)
	procCommandScrpt.generateCommandsAndWriteToScripts()
	outputFile = createOutputFile(procCommandScrpt.commandName,outputLocation)
	runTempScripts(outputFile,procCommandScrpt.tempFileNamePath)
	outputFile.close()
