#Author: Arko Basu [ HGST Inc.]
import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

def readDirectoryForScripts(dirName):
	"""This is the function which reads the directory for all the command scripts"""
	dictionaryOfCommandsScriptAbsolutePath = {}
	fileDictionary = {}
	for dirpath, dirnames, filenames in os.walk(dirName):
		index=1
		for files in filenames:
			if files.endswith(".xml"):
				fileDictionary[index] = files
				dictionaryOfCommandsScriptAbsolutePath[index] = os.path.join(dirName,files)
				index = index + 1
	return fileDictionary, dictionaryOfCommandsScriptAbsolutePath

def parseXMLScript(commandScript):
	"""This function parses the XML Script and returns the XML tree"""		
	#Import the XML Script File
	tree = ET.parse(commandScript)
	if tree is not None:
		print("Import Successful.")
	else:
		print("Malicious corrupted XML File. Please generate the XML file again")
	return tree

class modifyTree():
	def __init__(self,tree):
		self.tree = tree
		self.root = self.tree.getroot()
		self.grandChildMandTag = 'additionalMandDependantArgument'
		self.grandChildOptTag = 'additionalOptDependantArgument'

	def modifyAdditionalMandatoryGrandChild(self, commandArgList,modifyCommandArg, depMandCommand):
		newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildMandTag)
		for i in depMandCommand:
			newNode.append(commandArgList[i])
		#write the file or return the corrected tree
		
		
	def modifyAdditionalOptionalGrandChild(self, commandArgList,modifyCommandArg, depMandCommand):
		newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildOptTag)
		for i in depMandCommand:
			newNode.append(commandArgList[i])
		#write the file or return the corrected tree


def printArg(listOfArg):
	index = 0
	for i in listOfArg:
		text = i.text
		print(str(index) + ". " + text)
		index = index +1

def printArgsWithNAValues(listOfCommandArg, listOfIndexOfCommandsWithNAValues):
		print("Command Arguments with NA Values: ")		
		for val in listOfIndexOfCommandsWithNAValues:
			print(str(val) + ". " + str(listOfCommandArg[val].text))


def printBehaviourMappingTechnique():
	print("Please note the heirarchy of the behaviour mapping. Start with the lowest order of mapping.")


class command():
	def __init__(self,commandScript):
		self.commandScript = commandScript
		self.commandTree = parseXMLScript(self.commandScript)
		self.root = self.commandTree.getroot()
		self.command = self.root.text
		self.listOfCommandArg = []
		self.listOfCommandArgValues = []
		self.listOfIndexOfCommandsWithNAValues = []
	def getCommandArguments(self):
		for commandArg in self.root.iter('parameter'):
			self.listOfCommandArg.append(commandArg)

	def getCommandArgumentsValues(self):
		for commandArgVal in self.root.iter('parametervalues'):
			self.listOfCommandArgValues.append(commandArgVal)

	def verifyArgumentsAndTheirValuesLength(self):
		"""check for XML data integrity"""
		if not (len(self.listOfCommandArg)) == (len(self.listOfCommandArgValues)):
			print("Verify the XML Source. The number of command arguments and their values don't match.")

	def printCommandName(self):
		print("Command: " + str(self.command))
		
	def checkForNAValues(self):
		for indVal in range(len(self.listOfCommandArgValues)):
			if (self.listOfCommandArgValues[indVal].text) == 'NA':
				self.listOfIndexOfCommandsWithNAValues.append(indVal)
		
	
	def printRootBranch(self,branchNumber):
		print("Printing branch " + str(branchNumber) + " :")
		print(self.root[branchNumber].text)

	def processCommandsWithNAValues(self):
		print("In procedure for mapping commands with NA Values.")
		modTree = modifyTree(self.commandTree)
		define = 'Y'
		while define == 'Y':		
			try:
				printArgsWithNAValues(self.listOfCommandArg,self.listOfIndexOfCommandsWithNAValues)
				doesAdditionalArgument = (input("Does any of the command arguments from the above list take in additional parameters?(y/n): ")).upper()
				if doesAdditionalArgument == 'Y':
					printBehaviourMappingTechnique()
					index = int(input("Select the serial from the above list that you wish to proceed with: "))
					additionalArg = (input("Does the argument " + self.listOfCommandArg[index].text + " take in additional arguments? (Y/N): ")).upper()
					if additionalArg == 'Y':
						mandOpt = (input("(M)andatory/(O)ptional? : ")).upper()
						if mandOpt == 'M':
							printArg(self.listOfCommandArg)
							depArg = (input("Select the commands that go along with " + self.listOfCommandArg[index].text + " as mandatory additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
							depMandArg = [int (i) for i in depArg]
							modTree.modifyAdditionalMandatoryGrandChild(self.listOfCommandArg,index,depMandArg)
						elif mandOpt == 'O':
							printArg(listOfCommandArg.listOfCommandArg)
							depArg = (input("Select the commands that go along with " + self.listOfCommandArg[index].text + " as optional additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
							depOptArg = [int (i) for i in depArg]
							modTree.modifyAdditionalOptionalGrandChild(self.listOfCommandArg,index,depMandArg)
						else:
							print("Wrong option for kind of additional argument, selected. Try again.")
							continue
					
					elif additionalArg == 'N':
						print("XML modification not required.")
						continue
					else:
						print("Wrong option. Please try again")
						continue
				elif doesAdditionalArgument =='N':
					print("No additional arguments to map.")
					define = 'N'
				else:
					print("Please select the correct option.")
					continue
				
			except ValueError:
				print("Entered value is not a number. Please try again.")
			else:
				print("No exception thrown.")
				#modify the XML Tree
#		createTheNewModifiedXMLFile()

	


class processSoftwarePackageXMLs(object):
	def __init__(self, dirName):
		print("In procedure for dynamic mapping")
		self.dirName = dirName
		print("In " + self.dirName)
		self.fileDictionary, self.dictionaryOfCommandsScriptAbsolutePath = readDirectoryForScripts(self.dirName)		
		print(str(len(self.fileDictionary)) + " Scripts were found.")
		option = ''		
		while option != 'X':
			try:
				print(self.fileDictionary)
				option = (input("How do you wish to go about it? (E)xport/(I)mport data from output logs of one command to others? Or define any specific command argument (B)ehaviour? Type (X) to exit: ")).upper()
				if option == 'E':
					print("Under Development")
				
				elif option == 'I':
					print("Under Development")

				elif option == 'B':
					commandIndexOf = int(input("Enter the command serial from the above list that you wish to define argument dependencies on: "))
					treeForCommand = command(self.dictionaryOfCommandsScriptAbsolutePath[commandIndexOf])
					treeForCommand.getCommandArguments()
					treeForCommand.getCommandArgumentsValues()
					treeForCommand.verifyArgumentsAndTheirValuesLength()
					treeForCommand.printCommandName()
					treeForCommand.checkForNAValues()
#					printArg(treeForCommand.listOfCommandArg)
					if len(treeForCommand.listOfIndexOfCommandsWithNAValues) > 0 :
						treeForCommand.processCommandsWithNAValues()
					else:
						print("No command argument with NA values were found in the script.")


	
				elif option == 'X':
					break
				else:
					print("Wrong option selected. Please chose again.")
					option = (input("How do you wish to go about it? (E)xport/(I)mport data from output logs of one command to others? Or define command argument (B)ehaviour? Type (X) to exit: ")).upper() 				

			except ValueError:
				print("That is not a valid number. ")
			else:
				cont = (input("Dynamic Mapping procedure Ended. Do you wish to continue with Dynamic mapping?(y/n): ")).upper()
				if cont == 'N':
					print("Exiting Dynamic Mapping")
					break
				elif cont == 'Y':
					continue
		
