#author: Arko Basu[HGST Inc]
import os
import sys
import datetime
import xml.etree.ElementTree as ETProc
import subprocess
import ntpath


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

		for commandVal in listOfCommandArg[val].findall('importsFrom'):
			printString = printString + " Has imports tag from command: " + commandVal.text + "."
			break
		for commandVal in listOfCommandArg[val].iter('parametervalues'):
			if commandVal.text not in ['None', 'NA']:
				printString = printString + " Takes in values: " + commandVal.text
			else:
				break
#		for commandVal in listOfCommandArg[val].iter('importsFrom'):
#			printString = printString + " Has imports tag from command: " + commandVal.text + "."
#			break

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
	
	print("Please note that if a command takes mutiple arguments as dependant parameters. Pass them with semicolons(;) to generate similar test scripts.")

def getListOfValues(text):
	if ';' in text:
		listOfText = text.split(';')
#TODO:need to handle range
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

def extractData(paramText,output):
	listOfData = []
	for line in output.split(os.linesep):
		if paramText.upper() in line.upper():
			param = (line.split('='))[1].strip()
			listOfData.append(param)
	return list(set(listOfData))

def findPackageName(absolutePathOfCommandScript):
	head, tail = ntpath.split(absolutePathOfCommandScript)
	head1, tail1 = ntpath.split(head)
	head2, tail2 = ntpath.split(head1)
	

	return tail2
	

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
			self.listOfArgumentVal = commandArgVal.find('parametervalues')
		
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
		
	def getArguments(self):
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)
			self.listOfParameters.append(commandArg.text)

	def getArgumentsDet(self):
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
	

	def printDetailsOfCommandScript(self):
		print(self.listOfParameters)
		print(self.dictOfParameter)
		print(self.dictionaryOfMandParameters)
		print(self.dictionaryOfOptParameters)

	def generateCommandsAndWriteToScripts(self, outputLocation, tempLocation):
#		outputFile = createOutputFile(self.commandName,outputLocation)
#		tempFile = createTempFile(self.commandName, tempLocation)
		commandString = self.packageName + ' ' + self.commandName
		self.listOfOutputStrings.append(commanString)
#		tempFile.write(commandString)
#		tempFile.write('\n\n')
#		print(commandString)
		for parameter in self.listOfParameters:
			commandStringWithParam = commandString + ' ' + parameter
			tempFile.write(commandStringWithParam)
			tempFile.write('\n\n')
#			print(commandStringWithParam)
			if isinstance(self.dictOfParameter[parameter],str) :
				commandStringWithParamAndValues =  commandStringWithParam  
				if self.dictOfParameter[parameter] != '':
					commandStringWithParamAndValues = commandStringWithParamAndValues + ' ' + self.dictOfParameter[parameter]
					tempFile.write(commandStringWithParamAndValues)
					tempFile.write('\n\n')
#				print(parameter + 'S' + commandStringWithParamAndValues)
				if parameter in self.dictionaryOfMandParameters:
					processMandStrings(tempFile,self.dictOfMandParameters[parameter],commandStringWithParamAndValues)
				del commandStringWithParamAndValues
			elif isinstance(self.dictOfParameter[parameter],list):
				for paramVal in self.dictOfParameter[parameter]:
					#print(paramVal)
					commandStringWithParamAndValues = commandStringWithParam + ' ' + paramVal
					tempFile.write(commandStringWithParamAndValues)
					tempFile.write('\n\n')
#					print(parameter + 'L' + commandStringWithParamAndValues)
					if parameter in self.dictionaryOfMandParameters:
						for eachMandParam in self.dictionaryOfMandParameters[parameter]:
							cmdStrParamMand = commandStringWithParamAndValues
							if isinstance(eachMandParam,str):
								cmdStrParamMand = cmdStrParamMand + ' ' + eachMandParam + ' ' + str(self.dictOfParameter[eachMandParam])
								tempFile.write(cmdStrParamMand)
								tempFile.write('\n\n')
							elif isinstance(eachMandParam,list):
								for eachMandParamArg in eachMandParam:
									cmdStrParamMand = cmdStrParamMand + ' ' + eachMandParamArg + ' ' + str(self.dictOfParameter[eachMandParamArg])
								tempFile.write(cmdStrParamMand)
								tempFile.write('\n\n')
							del cmdStrParamMand
					del commandStringWithParamAndValues


				
def processMandStrings(tempFile,listOfMandArg,commandString):
	for eachMandArg in listOfMandArg:
		cmdStrParamMand = commandString
		if isinstance(eachMand,str):
			if not isinstance(self.dictOfParameter[eachMandParam],str):
				for eachMandParamVal in self.dictOfParameter[eachMandParam]:
					cmdStrParamMand = cmdStrParamMand + ' ' + eachMandParam + ' ' + eachMandParamVal
					tempFile.write(cmdStrParamMand)
					tempFile.write('\n\n')	
			else:
				cmdStrParamMand = cmdStrParamMand + ' ' + eachMandParam + ' ' + str(self.dictOfParameter[eachMandParam])
				tempFile.write(cmdStrParamMand)
				tempFile.write('\n\n')
		elif isinstance(eachMandParam,list):
			for eachMandParamArg in eachMandParam:
				cmdStrParamMand = cmdStrParamMand + ' ' + eachMandParamArg + ' ' + str(self.dictOfParameter[eachMandParamArg])
				tempFile.write(cmdStrParamMand)
				tempFile.write('\n\n')
			del cmdStrParamMand



	
class processElement():
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
		for paramValue in self.elem.findall('parametervalues'):
			if paramValue.text not in ['None','NA']:
				self.paramValues = getListOfValues(paramValue.text)
				break

		

def procXMLScrpt1(commandScript,outputLocation,tempLocation):
	procCommandScrpt = processCommandScriptMod(commandScript)
	procCommandScrpt.getArguments()
	procCommandScrpt.getArgumentsDet()
	procCommandScrpt.printDetailsOfCommandScript()
	procCommandScrpt.generateCommandsAndWriteToScripts(outputLocation,tempLocation)
	


