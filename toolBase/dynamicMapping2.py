#Author: Arko Basu [ HGST Inc.]
import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from . import utils as UTIL


def processCommandsWithNAValues(listOfCommandArg, listOfIndexOfCommandsWithNAValues,commandTree):
	define = 'Y'
	while define == 'Y':		
		modTree = modifyTree(commandTree, listOfCommandArg)
		try:
			print("Command Arguments with NA Values: ")
			UTIL.printArgsBasedOnIndex(listOfCommandArg,listOfIndexOfCommandsWithNAValues)
			doesAdditionalArgument = (input("Does any of the command arguments from the above list take in additional arguments?(y/n): ")).upper()
			if doesAdditionalArgument == 'Y':
				UTIL.printBehaviourMappingTechnique()
				index = int(input("Select the serial from the above list that you wish to proceed with: "))
				additionalArg = (input("Does the argument " + listOfCommandArg[index].text + " take in additional arguments? (Y/N): ")).upper()
				if additionalArg == 'Y':
					mandOpt = (input("(M)andatory/(O)ptional? : ")).upper()
					if mandOpt == 'M':
						UTIL.printList(listOfCommandArg)
						depArg = (input("Select the commands that go along with " + listOfCommandArg[index].text + " as mandatory additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depMandArg = [int (i) for i in depArg]
						modTree.modifyAdditionalMandatoryGrandChild(index,depMandArg)
					elif mandOpt == 'O':
						UTIL.printList(listOfCommandArg)
						depArg = (input("Select the commands that go along with " + listOfCommandArg[index].text + " as optional additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depOptArg = [int (i) for i in depArg]
						modTree.modifyAdditionalOptionalGrandChild(index,depMandArg)
					else:
						print("Wrong option for kind of additional argument, selected. Try again.")
						continue
				elif additionalArg == 'N':
					print("XML modification for " +listOfCommandArg[index].text + "not required.")
					continue
				else:
					print("Wrong option. Please try again")
					continue
			elif doesAdditionalArgument =='N':
				print("No additional arguments with NA values to map.")
				define = 'N'
			else:
				print("Please select the correct option.")
				continue
		except ValueError:
			print("Entered value is not a number. Please try again.")
		else:
			commandTree = modTree.tree
			del modTree
				
	return commandTree

def processCommandsWithNoneValues(listOfCommandArg, listOfIndex, commandTree,fileDictionary,dictionaryOfAbsPath):
	define = 'Y'
	while define == 'Y':
		modTree = modifyTree(commandTree, listOfCommandArg)
		try:
			print("Command Arguments with none values: ")
			UTIL.printArgsBasedOnIndex(listOfCommandArg, listOfIndex)
			option = (input("Do you wish to proceed defining argument behaviour for which the parameter values are found to be None for any of the commands from the above list?(y/n): ")).upper()
			if option == 'Y':
				index = int(input("Select the serial from the above list that you wish to proceed with: "))
				howTo = (input("Do you wish to (M)anually enter the values or tag other dependant commands that "+listOfCommandArg[index].text+" (I)mports the data from?: ")).upper()
				if howTo == 'M':
					manualEntry = input("Enter the values that you wish to pass on to the argument. PS: you can enter multiple values by separating them with a semicolon(;) : ")
					modTree.modifyManualArgument(index,manualEntry)
				elif howTo == 'I':
					print(fileDictionary)
					print("")
					importIndex = int(input("Select the serial number of command from the above list that the command " + listOfCommandArg[index].text + " imports data from: "))
					modTree.modifyImportArgument(index,dictionaryOfAbsPath[importIndex])
				else:
					print("Chose the correct option")
					continue

			elif option == 'N':
				print("Exiting procedure for defining any behaviour for arguments with no values.")
				define = 'N'
			else:
				print("Please select the correct option.")
				continue

		except ValueError:
			print("That is not a valid integer. Please try again.")
		else:
			print("No exceptions were raised.")
			commandTree = modTree.tree
			del modTree					
	return commandTree

def addExtraParameterValues(listOfCommandArg,commandTree):
	add = 'Y'
	while add == 'Y':
		modTree = modifyTree(commandTree, listOfCommandArg)
		try:
			add = (input("Do you wish to add any additional parameter values?(y/n) : ")).upper()
			if add == 'Y':
				UTIL.printArgsBasedOnIndex(listOfCommandArg, list(range(len(listOfCommandArg))))
				index = int(input("Select the serial from the above list that you wish to add parameter values to: "))
				addValue = input("Please enter the additional values that you wish to pass on to this argument. PS, you can pass mutiple values by entering it separated by a semiColon(;) : ")
				modTree.addValues(index,addValue)
				
			elif add == 'N':
				add = 'N'
				print("Exiting Procedure.")
				break
			else:
				print("Wrong input. Chose the correct option y/n. ")
				continue
		except ValueError:
			print("That is not a valid integer. Please try again.")
		except:
			print("Unexpected Error: " + sys.exc_info()[0])
		else:
			print("No exceptions were raised.")
			commandTree = modTree.tree
			del modTree
	return commandTree

def defineBehaviourOfCommand(commandScript,fileDictionary,dictionaryOfCommandsScriptAbsolutePath):
	treeForCommand = command(commandScript)
	treeForCommand.getCommandArguments()
	treeForCommand.getCommandArgumentsValues()
	treeForCommand.printCommandName()
	treeForCommand.checkForNAValues()
	if len(treeForCommand.listOfIndexOfCommandsWithNAValues) > 0 :
		treeForCommand.commandTree = processCommandsWithNAValues(treeForCommand.listOfCommandArg,treeForCommand.listOfIndexOfCommandsWithNAValues,treeForCommand.commandTree)
	else:
		print("No command argument with NA values were found in the script.")
	treeForCommand.checkForNoArgValues()
	if len(treeForCommand.listOfIndexOfCommandsWithNoneValue) > 0 :
		treeForCommand.commandTree = processCommandsWithNoneValues(treeForCommand.listOfCommandArg,treeForCommand.listOfIndexOfCommandsWithNoneValue,treeForCommand.commandTree,fileDictionary,dictionaryOfCommandsScriptAbsolutePath)
	else:
		print("No command argument with None values were found in the script.")
	treeForCommand.commandTree = addExtraParameterValues(treeForCommand.listOfCommandArg,treeForCommand.commandTree)
	


	return treeForCommand.commandTree


def defineExportBehaviour(commandIndexOf,commandIndexTo, dictionaryOfCommandsScriptAbsolutePath):
	listOfCommandsIndexString = commandIndexTo.split(';')
	listOfCommandsIndex = [int(i) for i in listOfCommandsIndexString]

	for eachIndexOfCommandScript in listOfCommandsIndex:
		treeForCommand = command(dictionaryOfCommandsScriptAbsolutePath[eachIndexOfCommandScript])
		treeForCommand.getCommandArguments()

	#continue tomorrow
	

class modifyTree():
	def __init__(self,tree, commandArgList):
		self.tree = tree
		self.root = self.tree.getroot()
		self.listOfCommandArg = commandArgList
		self.grandChildMandTag = 'additionalMandDependantArgument'
		self.grandChildOptTag = 'additionalOptDependantArgument'

	def modifyAdditionalMandatoryGrandChild(self,modifyCommandArg, depMandCommand):
		if self.root[modifyCommandArg].find(self.grandChildMandTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildMandTag)
			for i in depMandCommand:
				newNode.append(self.listOfCommandArg[i])
		else:
			for i in depMandCommand:
				(self.root[modifyCommandArg].find(self.grandChildMandTag)).append(self.listOfCommandArg[i])
	
				
	def modifyAdditionalOptionalGrandChild(self,modifyCommandArg, depMandCommand):
		if self.root[modifyCommandArg].find(self.grandChildOptTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildOptTag)
			for i in depMandCommand:
				newNode.append(self.listOfCommandArg[i])
		else:
			for i in depMandCommand:
				(self.root[modifyCommandArg].find(self.grandChildOptTag)).append(self.listOfCommandArg[i])

	def modifyManualArgument(self, index, manualEntry):
		for commandArgVal in self.root[index].iter('parametervalues'):
			commandArgVal.text = manualEntry

	def modifyImportArgument(self,index,commandName):
		for commandArg in self.root[index].iter('parametervalues'):
			commandArg.set('importsFrom',commandName)

	def addValues(self,index,addValue):
		for commandArg in self.root[index].iter('parametervalues'):
			commandArg.text = commandArg.text + ';' + addValue
		

class command():
	def __init__(self,commandScript):
		self.commandScript = commandScript
		self.commandTree = UTIL.parseXMLScript(self.commandScript)
		self.root = self.commandTree.getroot()
		self.command = self.root.text
		self.listOfCommandArg = []
		self.listOfCommandArgValues = []
		self.listOfIndexOfCommandsWithNAValues = []
		self.listOfIndexOfCommandsWithNoneValue = []

	def getCommandArguments(self):
		for commandArg in self.root:
			self.listOfCommandArg.append(commandArg)

	def getCommandArgumentsValues(self):
		for commandArg in self.listOfCommandArg:
			for commandArgVal in commandArg.iter('parametervalues'):
				self.listOfCommandArgValues.append(commandArgVal)
				break

	def printCommandName(self):
		print("Command: " + str(self.command))
		
	def checkForNAValues(self):
		for indVal in range(len(self.listOfCommandArgValues)):
			if (self.listOfCommandArgValues[indVal].text) == 'NA':
				self.listOfIndexOfCommandsWithNAValues.append(indVal)
		
	def checkForNoArgValues(self):
		for indVal in range(len(self.listOfCommandArgValues)):
			if (self.listOfCommandArgValues[indVal].text) == 'None':
				self.listOfIndexOfCommandsWithNoneValue.append(indVal)
		
class processSoftwarePackageXMLs(object):
	def __init__(self, dirName):
		print("In procedure for dynamic mapping")
		self.dirName = dirName
		print("In " + self.dirName)
		self.fileDictionary, self.dictionaryOfCommandsScriptAbsolutePath = UTIL.retreiveXMLFilesAndTheirAbsPath(self.dirName)		
		print(str(len(self.fileDictionary)) + " Scripts were found.")
		option = ''		
		while option != 'X':
			try:
				print(self.fileDictionary)
				print("")
				option = (input("How do you wish to go about it? (E)xport/(I)mport data from output logs from commands? Or define any specific command argument (B)ehaviour? Type (X) to exit: ")).upper()
				if option == 'E':
					print("Under Development")
					commandIndexOf = int(input("Enter the command serial from the above list that you wish to export output log from?: "))
					commandIndexTo = input("Enter the command serial from the above list that you wish to export output log to? PS: You can specify multiple command serials by separating them using a semicolon(;): ")
					defineExportBehaviour(commandIndexOf,commandIndexTo, self.dictionaryOfCommandsScriptAbsolutePath)
				
				elif option == 'I':
					print("Under Development")

				elif option == 'B':
					commandIndexOf = int(input("Enter the command serial from the above list that you wish to define argument dependencies on: "))
					modifiedTree = defineBehaviourOfCommand(self.dictionaryOfCommandsScriptAbsolutePath[commandIndexOf], self.fileDictionary, self.dictionaryOfCommandsScriptAbsolutePath)
					if modifiedTree is not None:
						UTIL.writeFile(self.dictionaryOfCommandsScriptAbsolutePath[commandIndexOf], modifiedTree)
	
				elif option == 'X':
					break
				else:
					print("Wrong option selected. Please chose again.")
					continue
			except ValueError:
				print("That is not a valid number. ")
			else:
				cont = (input("Dynamic Mapping procedure ended. Do you wish to continue with Dynamic mapping?(y/n): ")).upper()
				if cont == 'N':
					print("Exiting Dynamic Mapping")
					break
				elif cont == 'Y':
					continue
		
