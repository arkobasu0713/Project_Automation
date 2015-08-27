#author: Arko Basu[HGST Inc]
import os
import sys
import datetime
import xml.etree.ElementTree as ETProc
import subprocess


def retreiveXMLFilesAndTheirAbsPath(XMLFolder):

	"""This function walks through the Original XML Scripts folder and returns two dictionaries of files and their absolute path corresponding to serial numbers as keys for the programs to refer to."""

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

def CreateDirectoryForSoftwarePackage(softwarePackageName):

	"""This function creates a folder for software package imported through data source in workFiles/processedFiles. If the folder already exists, it creates a separate folder for XML scripts with data time apended."""

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

	"""This function creates an XML file for an individual command processed in the originating master XML Data Source."""

	fileName = commandName + ".xml"
	filePath = os.path.join(XMLScriptDirectory,fileName)
	file = open(filePath, 'wb')
	print("File " + filePath +" for command, " + commandName +" created")
	return file

def parseXMLScript(commandScript):

	"""This function parses the XML Script and returns the XML tree"""		

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
		for commandVal in listOfCommandArg[val].iter('parametervalues'):
			if commandVal.text not in ['None', 'NA']:
				printString = printString + " Takes in values: " + commandVal.text
			else:
				break
		for commandVal in listOfCommandArg[val].iter('importsFrom'):
			printString = printString + " Has imports tag from command: " + commandVal.text + "."
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

def getListOfValues(text):
	if ';' in text:
		listOfText = text.split(';')
		return listOfText
	else:
		return text

def writeFile(pathForFile,modifiedTree):

	"""This function simply removes the existing file in the directory and recreates it with the modified tree structure"""

	os.remove(pathForFile)
	modifiedTree.write(pathForFile)

def procXMLScrpt(FileName,packageName):
	procCommandScrpt = processCommandScript(FileName,packageName)
	procCommandScrpt.getArguments()
	procCommandScrpt.getArgumentValues()
	procCommandScrpt.processArguments()

	return procCommandScrpt

def createOutputFile(commandName,outputLocation):
	now = datetime.datetime.now()
	fileName = commandName + '_' + now.strftime("%Y%m%d_%H:%M")
	fileNamePath = os.path.join(outputLocation, fileName)
	file = open(fileNamePath, 'wt')

	return file

def RunScript(commandString):
	p = subprocess.Popen(commandString,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
	return p

def runImportScript(commandScript,packageName):
	procImpScript = processCommandScript(commandScript,packageName)
	procImpScript.getArguments()
	commandString = procImpScript.packageName + ' ' + procImpScript.commandName
	p = RunScript(commandString)
	return p

def writeAndRun(outputFile,commandString):
	outputFile.write(commandString)
	outputFile.write("\n")
#	print(commandString)
	p = RunScript(commandString)
	output, err = p.communicate()
	if output.decode('ascii') == '':
		outputFile.write(err.decode('ascii'))
#		print(err.decode('ascii'))
	else:
		outputFile.write(output.decode('ascii'))
#		print(output.decode('ascii'))
	outputFile.write("\n")
	

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
			del modCommandString1
		elif isinstance(comdScrpt.dictionaryOfArgumentsAndTheirValues[elements],list):
			for val in comdScrpt.dictionaryOfArgumentsAndTheirValues[elements]:
				modCommandString2 = modCommandString + ' ' + val
				writeAndRun(outputFile,modCommandString2)
				del modCommandString2
		del modCommandString

	outputFile.close()

def createTempFile(commandName,tempLocation):
	now = datetime.datetime.now()
	fileName = commandName + '_' + now.strftime("%Y%m%d_%H:%M")
	fileNamePath = os.path.join(tempLocation, fileName)
	file = open(fileNamePath, 'wt')

	return file
	
def writeTempFile(commandString,tempFile):
	tempFile.write(commandString)
	tempFile.write('\n\n')

def generateAndRunScripts2(comdScrpt,outputLocation, tempLocation, packageName):
	#outputFile = createOutputFile(comdScrpt.commandName,outputLocation)
#	tempFile = createTempFile(comdScrpt.commandName, tempLocation)
	commandString = packageName + ' ' +comdScrpt.commandName
	print(commandString)
#	writeTempFile(commandString,tempFile)
	for argument in comdScrpt.listOfArguments:
		print(commandString + argument.text)
		mCommandString = commandString + argument.text
#		writeTempFile(mCommandString,tempFile)
		processParam(argument)


def processParam(argument):
	for argumentChild in argument:
		if argumentChild.tag == 







	"""	for argument in comdScrpt.dictionaryOfArgumentParameterValues:
			modCommandString = commandString + ' ' + argument
			writeTempFile(modCommandString,tempFile)
			if comdScrpt.dictionaryOfArgumentParameterValues[argument] == '':
				if comdScrpt.dictionaryOfArgumentImportsFrom[argument] != ''
					#run and extract data
	



	
			if isinstance(comdScrpt.dictionaryOfArgumentParameterValues[argument],str):
				modCommandString = modCommandString + ' ' + comdScrpt.dictionaryOfArgumentParameterValues[argument]
				writeTempFile(modCommandString,tempFile)
			elif isinstance(comdScrpt.dictionaryOfArgumentParameterValues[argument],list):
				for val in comdScrpt.dictionaryOfArgumentParameterValues[argument]:
					modCommandString1 = modCommandString + ' ' + val
					writeTempFile(modCommandString1,tempFile)
					del modCommandString1
			del modCommandString
	
		#outputFile.close()
	"""

def extractData(paramText,output):
	listOfData = []
	for line in output.split(os.linesep):
		if paramText.upper() in line.upper():
			param = (line.split('='))[1].strip()
			listOfData.append(param)
	return listOfData

class processCommandScript():
	def __init__(self,fileName,packageName):
		self.fileName = fileName
		self.packageName = packageName
		self.tree = parseXMLScript(self.fileName)
		self.root = self.tree.getroot()
		self.listOfArguments = []
		self.listOfArgumentVal = []
		self.commandName = self.root.text
		self.dictOfMandArg = {}
		self.dictOfOptArg = {}
		self.dictionaryOfArgumentsAndTheirValues = {}
		self.dictOfParamImport = {}

	def getArguments(self):
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)
		
	def getArgumentValues(self):
		for commandArgVal in self.listOfArguments:
			for val in commandArgVal.iter('parametervalues'):
				self.listOfArgumentVal.append(val)
				break
		
	def processListOfArguments(self):
		for index in range(len(self.listOfArguments)):
			commandtext = self.listOfArguments[index].text
			self.dictionaryOfArgumentsAndTheirValues[commandtext] = getListOfValues(self.listOfArgumentVal[index].text)

	def processArguments(self):
		for element in self.listOfArguments:
			paramText = element.text
			for subElem in element.iter('parametervalues'):
				if subElem.text == 'None':
					for subElemImport in element.iter('importsFrom'):
						print("Imports From: " + subElemImport.text)
						p = runImportScript(subElemImport.text,self.packageName)
						output, err = p.communicate()
						if output.decode('ascii') == '':
							print('Import Command for ' + paramText + "Had a Run Error as followed: " + err.decode('ascii'))
						else:
							self.dictionaryOfArgumentsAndTheirValues[paramText] = extractData(paramText.strip('-'),output.decode('ascii'))
						self.dictOfParamImport[paramText] = subElemImport.text
					break
				else:
					self.dictionaryOfArgumentsAndTheirValues[paramText] = getListOfValues(subElem.text)
					break
			for subElem in element.iter('additionalMandDependantArgument'):
				self.dictOfMandArg[paramText] = subElem
				break
			for subElem in element.iter('additionalOptDependantArgument'):
				self.dictOfOptArg[paramText] = subElem
				break

		print(self.dictionaryOfArgumentsAndTheirValues)
		print(self.dictOfMandArg)
		print(self.dictOfOptArg)
		print(self.dictOfParamImport)



class processCommandScriptMod():
	def __init__(self,fileName,packageName):
		self.fileName = fileName
		self.packageName = packageName
		self.tree = parseXMLScript(self.fileName)
		self.root = self.tree.getroot()
		self.commandName = self.root.text
		self.listOfArguments = []
		self.dictionaryOfArgumentParameterValues = {}
		self.dictionaryOfArgumentImportsFrom = {}
		self.dictionaryOfArgumentAdditionalMandArg ={}
		self.dictionaryOfArgumentAdditionalOptArg = {}
		


	def getArguments(self):
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)


	def processArgumentTree(self):
		for element in self.listOfArguments:
			elem = Element(element)
			elem.getParamValue()
			if elem.elementParamValue in ['None','NA','']:
				self.dictionaryOfArgumentParameterValues[elem.elementText] = ''
				elem.getImportsFrom()
				self.dictionaryOfArgumentImportsFrom[elem.elementText] = elem.elementImportsFrom
				elem.getMandArg()
				self.dictionaryOfArgumentAdditionalMandArg[elem.elementText] = elem.elementMandArg
				elem.getOptArg()
				self.dictionaryOfArgumentAdditionalOptArg[elem.elementText] = elem.elementOptArg
			else:
				self.dictionaryOfArgumentParameterValues[elem.elementText] = getListOfValues(elem.elementParamValue)

#		print(self.dictionaryOfArgumentParameterValues)
#		print(self.dictionaryOfArgumentImportsFrom)
#		print(self.dictionaryOfArgumentAdditionalMandArg)
#		print(self.dictionaryOfArgumentAdditionalOptArg)





class Element():
	def __init__(self,element):
		self.element = element
		self.numOfChildren = len(self.element)
		self.elementText = self.element.text
		self.elementTag = self.element.tag
		self.elementParamValue = ''
		self.elementImportsFrom = ''
		self.elementMandArg = ''
		self.elementOptArg = '' 
	
	def getParamValue(self):
		for paramValue in self.element.iter('parametervalues'):
			self.elementParamValue = paramValue.text
			break
	def getImportsFrom(self):
		for eachChild in range(self.numOfChildren):
			if self.element[eachChild].tag == 'importsFrom':
				self.elementImportsFrom = self.element[eachChild].text
		
		
	def getMandArg(self):
		for eachChild in range(self.numOfChildren):
			if self.element[eachChild].tag == 'additionalMandDependantArgument':
				self.elementMandArg = self.element[eachChild]

	def getOptArg(self):
		for eachChild in range(self.numOfChildren):
			if self.element[eachChild].tag == 'additionalOptDependantArgument':
				self.elementOptArg = self.element[eachChild]
