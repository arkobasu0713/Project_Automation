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

	root = tree.getroot()
	return root


def createModifyXMLScriptDirectory(originalXMLScriptDirectory):
	modDir = os.path.join(originalXMLScriptDirectory,'..','modifiedXMLScripts')
	if not os.path.exists(modDir):
		os.mkdir(modDir)
		print("Directory for modified scripts build at: " + modDir)
	else:
		print("Directory already exists")
	return modDir

def mapDependencyForNA(commandArg,k):
	depIndv = input("The command argument " + commandArg[k] + " has NA argument values? Does it take additional arguments?(Y/N): ")
	if depIndv.upper() == 'Y':
		for i,j in enumerate(commandArg):
			print(str(i) + '. ' + j)
		addArg = input("Select the argument from the above list that the " + commandArg[k] + " takes as an additional input.(You can tag multiple arguments by passing them with a comma(,)): ")
	

class modifyXMLScripts(object):
	def __init__(self, dirName,optionSelected):
		self.dirName = dirName

	def addArgsBehaviour(self,commandScript):
		self.rootElement = parseXMLScript(commandScript)
		self.commandArg = []
		self.commandArgVal = []
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
					mapDependencyForNA(self.commandArg,i)





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
		for dirpath, dirnames, filenames in os.walk(self.dirName):
			index=1
			for files in filenames:
				if files.endswith(".xml"):
					print(str(index) + ". " + files)
					dictionaryOfCommands[index] = os.path.join(dirName,files)
					index = index + 1
		commandIndexFrom = 0
		commandIndexTo = []
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
						modifiedScript.addArgsBehaviour(dictionaryOfCommands[commandIndexOf])
					elif genericOrSpecific.upper() == 'G':
						print("Generic Search of command suits for similar arguments.")
					cont = input("Do you wish to continue with another suit of mapping(Y/N)?")
					if cont.upper() == 'N':
						break
					else:
						continue
			except ValueError:
				print("That is not a valid number. ")
			else:
				print("Wrong option selected.")

			
#		modifyXMLScripts(dictionaryOfCommands, dirName, commandIndexFrom, commandIndexTo)
