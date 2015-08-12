#Author: Arko Basu [ HGST Inc.]
import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

def parseXMLScript(commandScript):
		
	#Import the XML Script File
	tree = ET.parse(commandScript)
	if tree is not None:
		print("Import Successful.")
	else:
		print("Malicious corrupted XML File. Please generate the XML file again")

	
	return tree


def createModifyXMLScriptDirectory(originalXMLScriptDirectory):
	modDir = os.path.join(originalXMLScriptDirectory,'..','modifiedXMLScripts')
	if not os.path.exists(modDir):
		os.mkdir(modDir)
		print("Directory for modified scripts build at: " + modDir)
	else:
		print("Directory already exists")
	return modDir

def mapDependencyForNA(commandArg,k):
	devIndv = (input("The command argument " + commandArg[k] + " has NA argument values? Does it take additional mandatory/optional arguments?(Y/N): ")).upper()
	depMandCommand = None
	depOptCommand = None
	while devIndv == 'Y':
		print('inside while loop')
		try:
			if devIndv.upper() == 'Y':
				for i,j in enumerate(commandArg):
					print(str(i) + '. ' + j)
				specifyMandOpt = input("(M)andatory/(O)ptional?: ")
				if specifyMandOpt.upper() == 'M':
					addMandArg = input("Select the arguments from the above list that the " + commandArg[k] + " takes as an additional(mandatory) input.(You can tag multiple arguments by passing them with a comma(,)): ").split(',')
					depMandCommand = [int (i) for i in addMandArg]
					print(depMandCommand)
				elif specifyMandOpt.upper() == 'O':
					addOptArg = input("Select the arguments from the above list that the " + commandArg[k] + " takes as an additional(optional) input.(You can tag multiple arguments by passing them with a comma(,)): ").split(',')
					depOptCommand = [int (i) for i in addOptArg]
				else:
					print("Please chose correct option")
			else:
				break
		except TypeError:
			print("Wrong Input. Try again")
		else:
			devIndv = input("The command argument " + commandArg[k] + " has NA argument values? Does it take additional mandatory/optional arguments?(Y/N): ")
			devIndv = devIndv.upper()

	return depMandCommand, depOptCommand

def modifyXMLSource(commandScript, depCommand, commandArg,i):
	tree = parseXMLScript(commandScript)
	root = tree.getroot()
	childtag = 'dependantArg'
	for commands in root.iter('parameter'):
		tag = commands.tag
		text = commands.text
		if text == commandArg[i]:
			for j in depCommand:
				grandchild2 = ET.SubElement(commands,childtag)
				grandchild2.text = commandArg[j]
	
	os.remove(commandScript)			
	tree.write(commandScript)			

class modifyXMLScripts(object):
	def __init__(self, dirName,optionSelected):
		self.dirName = dirName

	def addArgsBehaviour(self,commandScript,modXMLDir):
		self.tree = parseXMLScript(commandScript)
		self.rootElement = self.tree.getroot()
		self.commandArg = []
		self.commandArgVal = []
		self.modXMLDir = modXMLDir
		for command in self.rootElement.iter('commandName'):
			commandName = command.text
		print(commandName)
		self.dictionaryOfCommands = {}
		for child in self.rootElement.iter('parameter'):
			self.commandArg.append(child.text)
		for child in self.rootElement.iter('parametervalues'):
			self.commandArgVal.append(child.text)
		
		lenCommands = len(self.commandArg)
		lenCommandsVal = len(self.commandArgVal)

		if not lenCommands == lenCommandsVal:
			print("Arguments, and their corresponding parameters are not matching. Please check Original XML Script for inconsistant child and grandchild data.")
		else:
			for i in range(lenCommands):
				if self.commandArgVal[i] == 'NA':
					depMandCommand, depOptCommand = mapDependencyForNA(self.commandArg,i)
					if depMandCommand is not None:
						#print(self.commandArg[depCommand])
						modifyXMLSource(commandScript, depMandCommand, self.commandArg,i)




				self.dictionaryOfCommands[self.commandArg[i]] = self.commandArgVal[i]

		print("Command Dictionary: ")
		print(self.dictionaryOfCommands)

	
		"""
		print("Command arguments found in script: ")
		print(self.commandArg)
		print("Corresponding argument values found in script: ") 
		print(self.commandArgVal)
"""


		

class processSoftwarePackageXMLs(object):
	def __init__(self, dirName):
		print("In procedure for dynamic mapping")
		self.dirName = dirName
		print("In " + self.dirName)
		self.modifiedXMLScriptsDirectory = createModifyXMLScriptDirectory(self.dirName)
		print("Command Scripts found inside the package folder: ")
		dictionaryOfCommands = {}
		fileDictionary = {}
		for dirpath, dirnames, filenames in os.walk(self.dirName):
			index=1
			for files in filenames:
				if files.endswith(".xml"):
					fileDictionary[index] = files
					dictionaryOfCommands[index] = os.path.join(dirName,files)
					index = index + 1
		commandIndexFrom = 0
		commandIndexTo = []
		print(fileDictionary)
		while True:
			try:
				option = input("How do you wish to go about it? (E)xport/(I)mport data from output logs of one command to others? Or define command argument (B)ehaviour?:  ")
				if option.upper() == 'E':
					commandIndexFrom = int(input("Enter the command serial from the above list that you wish to extract/export data from:  "))
					commandIndexTo = (input("Enter the command serial from the above list that you wish to pass the data to [PS: This can have a multiple value passed with separated with (,):  ")).split(',')
					commandIndexTo = [int (i) for i in commandIndexTo]
					print(commandIndexTo)
					break
				elif option.upper() == 'I':
					commandIndexTo = int(input("Enter the command serial from the above list that you wish to import data into [PS: This can have a multiple value passed with separated with (,):  "))
					commandIndexFrom = (input("Enter the command serial from the above list that you wish to export/extract data from:  ")).split(',')
					commandIndexTo = [int (i) for i in commandIndexTo]
					print(commandIndexTo)
					break
				elif option.upper() == 'B':
					modifiedScript = modifyXMLScripts(self.modifiedXMLScriptsDirectory, option.upper())
					genericOrSpecific = input("Okay. Do you wish to define any (G)eneric command argument behaviour in all of the commands, or any (S)pecific command in particular: ")
					if genericOrSpecific.upper() == 'S':
						commandIndexOf = int(input("Enter the command serial from the above list that you wish to define argument dependencies on: "))
						modifiedScript.addArgsBehaviour(dictionaryOfCommands[commandIndexOf],self.modifiedXMLScriptsDirectory)
						cont = input("Do you wish to continue with another suit of mapping(Y/N)?")
						if cont.upper() == 'N':
							break
						else:
							print("List of command scripts: ")
							print(fileDictionary)
							continue
					elif genericOrSpecific.upper() == 'G':
						print("Generic Search of command suits for similar arguments.")
						if cont.upper() == 'N':
							break
						else:
							print("List of command scripts: ")
							print(fileDictionary)
							continue
					
			except ValueError:
				print("That is not a valid number. ")
			else:
				print("Wrong option selected.")

			
#		modifyXMLScripts(dictionaryOfCommands, dirName, commandIndexFrom, commandIndexTo)





