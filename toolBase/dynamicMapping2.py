#Author: Arko Basu [ HGST Inc.]
import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from . import utils as UTIL


def processCommandsWithNAValues(treeForCommand):

	"""This function processes the tree extracted from the command script to modify the behaviour of command arguments with "NA" parametervalues"""

	define = 'Y'
	while define == 'Y':		
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		try:
			print("Command Arguments with NA Values: ")
			UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, treeForCommand.listOfIndexOfCommandsWithNAValues)
			doesAdditionalArgument = (input("Does any of the command arguments from the above list take in additional arguments?(y/n): ")).upper()
			if doesAdditionalArgument == 'Y':
				UTIL.printBehaviourMappingTechnique()
				index = int(input("Select the serial from the above list that you wish to proceed with: "))
				additionalArg = (input("Does the argument " + treeForCommand.listOfCommandArg[index].text + " take in additional arguments? (Y/N): ")).upper()
				if additionalArg == 'Y':
					mandOpt = (input("(M)andatory/(O)ptional? : ")).upper()
					if mandOpt == 'M':
						UTIL.printList(treeForCommand.listOfCommandArg)
						UTIL.printDynamicMappingTechnique()
						depArg = (input("Select the commands that go along with " + treeForCommand.listOfCommandArg[index].text + " as mandatory additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depMandArg = [int (i) for i in depArg]
						modTree.modifyAdditionalMandatoryGrandChild(index,depMandArg)
					elif mandOpt == 'O':
						UTIL.printList(treeForCommand.listOfCommandArg)
						depArg = (input("Select the commands that go along with " + treeForCommand.listOfCommandArg[index].text + " as optional additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depOptArg = [int (i) for i in depArg]
						modTree.modifyAdditionalOptionalGrandChild(index,depOptArg)
					else:
						print("Wrong option for kind of additional argument, selected. Try again.")
						continue
				elif additionalArg == 'N':
					print("XML modification for " + treeForCommand.listOfCommandArg[index].text + "not required.")
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
			treeForCommand.commandTree = modTree.tree
			del modTree
				
	return treeForCommand.commandTree



def processCommandsWithNoneValues(treeForCommand,fileDictionary,dictionaryOfAbsPath):

	"""This function processes the tree extracted from the command script to modify the behaviour of command arguments with "NONE" parametervalues"""

	define = 'Y'
	while define == 'Y':
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		try:
			print("Command Arguments with None Values: ")
			UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, treeForCommand.listOfIndexOfCommandsWithNoneValue)
			option = (input("Do you wish to proceed defining parameter values or their behaviour for which the parameter values are found to be None for any of the commands from the above list?(y/n): ")).upper()
			if option == 'Y':
				index = int(input("Select the serial from the above list that you wish to proceed with: "))
				howTo = (input("Do you wish to (M)anually enter the values or tag other dependant commands that "+ treeForCommand.listOfCommandArg[index].text+" (I)mports the data from?: ")).upper()
				if howTo == 'M':
					manualEntry = input("Enter the values that you wish to pass on to the argument. PS: you can enter multiple values by separating them with a semicolon(;) : ")
					modTree.modifyManualArgument(index,manualEntry)
				elif howTo == 'I':
					print(fileDictionary)
					print("")
					importIndex = int(input("Select the serial number of command from the above list that the command " + treeForCommand.listOfCommandArg[index].text + " imports data from: "))
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
			treeForCommand.commandTree = modTree.tree
			del modTree					
	return treeForCommand.commandTree


def addExtraParameterValues(treeForCommand):

	"""This function processes a tree extracted from a command script to add any additional parameter values to any of the command arguments at the discretion of the user/tester"""

	add = 'Y'
	while add == 'Y':
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		print(str(len(treeForCommand.listOfCommandArg)) + " command arguments found in the script: ")
		UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
		try:
			add = (input("Do you wish to add any additional parameter values?(y/n) : ")).upper()
			if add == 'Y':
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
			treeForCommand.commandTree = modTree.tree
			del modTree
	return treeForCommand.commandTree

def multipleDependency(treeForCommand):
	add = 'Y'
	while add == 'Y':
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		try:
			add = (input("Do you wish to define multiple dependency in one go?(y/n) : ")).upper()
			if add == 'Y':
				UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
				index = int(input("Select the serial from the above list that you wish to define multiple dependency on: "))
				addTo = [int(i) for i in ((input("Chose from the above list of arguments that you wish to add the command argument " + treeForCommand.listOfCommandArg[index].text + " as dependant argument.(PS, you can add multiple arguments by separating them by a semicolon): ")).split(';'))]
				for singleAddToIndex in addTo:
					pas = [index]
					choice = input(str(treeForCommand.root[index].text) + " (M)andatory/(O)ptional dependant argument to " + str(treeForCommand.root[singleAddToIndex].text) + " ").upper()
					if choice == 'M':
						modTree.modifyAdditionalMandatoryGrandChild(singleAddToIndex,pas)
					elif choice == 'O':
						modTree.modifyAdditionalOptionalGrandChild(singleAddToIndex,pas)
					else:
						print("Wrong option selected. Please start again.")
						break

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
			treeForCommand.commandTree = modTree.tree
			del modTree

	return treeForCommand.commandTree

def checkAllCommands(treeForCommand,fileDictionary,dictionaryOfCommandsScriptAbsolutePath):
	add = 'Y'
	while add == 'Y':
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		try:
			add = (input("Do you wish to define any other dependency for command arguments found in the script?(y/n) : ")).upper()
			if add == 'Y':
				UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
				index = int(input("select the serial of the command that you want to add dependency from the above list: "))
				if index > len(treeForCommand.listOfCommandArg) or index < 0:
					print("Invalid serial selected. Please try again.")
					continue
				else:
					choice = (input("What do you wish to perform? Add (M)andatory/(O)ptional dependant argument, (A)dd extra argument value, or add (I)mport script value. Press (X) to exit procedure: ")).upper()
					if choice == 'M':
						UTIL.printList(treeForCommand.listOfCommandArg)
						depArg = (input("Select the commands that go along with " + treeForCommand.listOfCommandArg[index].text + " as mandatory additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depMandArg = [int (i) for i in depArg]
						modTree.modifyAdditionalMandatoryGrandChild(index,depMandArg)
					elif choice == 'O':
						UTIL.printList(treeForCommand.listOfCommandArg)
						depArg = (input("Select the commands that go along with " + treeForCommand.listOfCommandArg[index].text + " as optional additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depOptArg = [int (i) for i in depArg]
						modTree.modifyAdditionalOptionalGrandChild(index,depOptArg)
					elif choice == 'A':
						UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
						addValue = input("Please enter the additional values that you wish to pass on to this argument. PS, you can pass mutiple values by entering it separated by a semiColon(;) : ")
						modTree.addValues(index,addValue)
					elif choice == 'I':
						print(fileDictionary)
						print("")
						importIndex = int(input("Select the serial number of command from the above list that the command " + treeForCommand.listOfCommandArg[index].text + " imports data from: "))
						modTree.modifyImportArgument(index,dictionaryOfAbsPath[importIndex])
					elif choice == 'X':
						add = 'N'
						print("Exit Procedure checkAllCommands")
						break	
					else:
						print("Wrong option selected. Try again")
						continue
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
			treeForCommand.commandTree = modTree.tree
			del modTree
	



	return treeForCommand.commandTree

def defineBehaviourOfCommand(commandScript,fileDictionary,dictionaryOfCommandsScriptAbsolutePath):
	treeForCommand = command(commandScript)
	treeForCommand.getCommandArguments()
	treeForCommand.getCommandArgumentsValues()
	treeForCommand.printCommandName()
	treeForCommand.checkForNAValues()
	treeForCommand.checkForNoArgValues()

	treeForCommand.commandTree = addExtraParameterValues(treeForCommand)
	treeForCommand.commandTree = multipleDependency(treeForCommand)

	if len(treeForCommand.listOfIndexOfCommandsWithNoneValue) > 0 :
		treeForCommand.commandTree = processCommandsWithNoneValues(treeForCommand,fileDictionary,dictionaryOfCommandsScriptAbsolutePath)
	else:
		print("No command argument with None values were found in the script.")	

	if len(treeForCommand.listOfIndexOfCommandsWithNAValues) > 0 :
		treeForCommand.commandTree = processCommandsWithNAValues(treeForCommand)
	else:
		print("No command argument with NA values were found in the script.")
	
	treeForCommand.commandTree = checkAllCommands(treeForCommand,fileDictionary,dictionaryOfCommandsScriptAbsolutePath)
	
	

	
	
	return treeForCommand.commandTree


def defineExportBehaviour(commandIndexOf,commandIndexTo, exportCommand, dictionaryOfCommandsScriptAbsolutePath):
	listOfCommandsIndexToString = commandIndexTo.split(';')
	listOfCommandsIndexTo = [int(i) for i in listOfCommandsIndexToString]

	for eachIndexOfCommandScript in listOfCommandsIndexTo:
		treeForCommand = command(dictionaryOfCommandsScriptAbsolutePath[eachIndexOfCommandScript])
		treeForCommand.getCommandArguments()
		print("Command arguments found in " + treeForCommand.command + " :")
		UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
		addTo = (input("Chose from the above list of arguments that you wish to add the command " + exportCommand.rstrip('.xml') + " for export log to(PS, you can add multiple arguments by separating them by a semicolon): ")).split(';')
		addTo = [int(i) for i in addTo]
		for indvAdd in addTo:
		#	for commandArg in treeForCommand.root[indvAdd].iter('parametervalues'):
		#		commandArg.set('importsFrom',dictionaryOfCommandsScriptAbsolutePath[commandIndexOf])


			if treeForCommand.root[indvAdd].find('importsFrom') is None:
				newNode = ET.SubElement(treeForCommand.root[indvAdd], 'importsFrom')
				newNode.text = dictionaryOfCommandsScriptAbsolutePath[commandIndexOf]
			else:
				print("Modifying already existing import tag.")
				(treeForCommand.root[indvAdd].find('importsFrom')).text = commandName

		UTIL.writeFile(dictionaryOfCommandsScriptAbsolutePath[eachIndexOfCommandScript], treeForCommand.commandTree)

	#continue tomorrow
	

class modifyTree():
	def __init__(self,tree, commandArgList):
		self.tree = tree
		self.root = self.tree.getroot()
		self.listOfCommandArg = commandArgList
		self.grandChildMandTag = 'additionalMandDependantArgument'
		self.commandTag = 'command'
		self.grandChildOptTag = 'additionalOptDependantArgument'
		self.importsFromTag = 'importsFrom'

	def modifyAdditionalMandatoryGrandChild(self,modifyCommandArg, depMandCommand):
		if self.root[modifyCommandArg].find(self.grandChildMandTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildMandTag)
			for i in depMandCommand:
				childNode = ET.SubElement(newNode,self.commandTag)
				childNode.text = self.listOfCommandArg[i].text
		else:
			for i in depMandCommand:
				childNode = ET.SubElement(self.root[modifyCommandArg].find(self.grandChildOptTag),self.commandTag)
				childNode.text = self.listOfCommandArg[i].text
	
				
	def modifyAdditionalOptionalGrandChild(self,modifyCommandArg, depMandCommand):
		if self.root[modifyCommandArg].find(self.grandChildOptTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildOptTag)
			for i in depMandCommand:
				childNode = ET.SubElement(newNode,self.commandTag)
				childNode.text = self.listOfCommandArg[i].text
		else:
			for i in depMandCommand:
				childNode = ET.SubElement(self.root[modifyCommandArg].find(self.grandChildOptTag),self.commandTag)
				childNode.text = self.listOfCommandArg[i].text

	def modifyManualArgument(self, index, manualEntry):
		for commandArgVal in self.root[index].iter('parametervalues'):
			commandArgVal.text = manualEntry

	def modifyImportArgument(self,index,commandName):
#		for commandArg in self.root[index].iter('parametervalues'):
#			commandArg.set('importsFrom',commandName)

		if self.root[index].find(self.importsFromTag) is None:
			newNode = ET.SubElement(self.root[index], self.importsFromTag)
			newNode.text = commandName
		else:
			print("Modifying already existing import tag.")
			(self.root[index].find(self.importsFromTag)).text = commandName

	def addValues(self,index,addValue):
		for commandArg in self.root[index].iter('parametervalues'):
			if commandArg.text == 'None':
				commandArg.text = addValue
			else:
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
		self.dictOfCommandImportArg = {}
		self.dictOfCommandOptArgument = {}
		self.listOfCommandsWithNAValues = []
		self.listOfCommandsWithNoneValue = []

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
				self.dictOfCommandImportArg[self.listOfCommandArg[indVal].text] = self.listOfCommandArgValues[indVal].attrib

	def checkForDepArguments(self):
		for commandArg in self.listOfCommandArg:
			for commandDepArg in commandArg.iter('additionalMandDependantArgument'):
				self.listOfCommandDepArgument.append(commandDepArg)
				break

	def checkForOptArguments(self):
		for commandArg in self.listOfCommandArg:
			for commandOptArg in commandArg.iter('additionalOptDependantArgument'):
				self.listOfCommandOptArgument.append(commandOptArg)
				break

	def checkForImportDependency(self):
		for commandArg in self.listOfCommandArgValues:
			print(commandArg.attrib)
		
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
					commandIndexOf = int(input("Enter the command serial from the above list that you wish to export output log from?: "))
					commandIndexTo = input("Enter the command serial from the above list that you wish to export output log to? PS: You can specify multiple command serials by separating them using a semicolon(;): ")
					defineExportBehaviour(commandIndexOf,commandIndexTo, self.fileDictionary[commandIndexOf], self.dictionaryOfCommandsScriptAbsolutePath)
				
				elif option == 'I':

					print("Under Development")
#					commandIndexOf = int(input("Enter the command serial from the above list.: "))
#					commandScrptTree = command(self.dictionaryOfCommandsScriptAbsolutePath[commandIndexOf])
#					commandScrptTree.getCommandArguments()
#					commandScrptTree.getCommandArgumentsValues()
#					commandScrptTree.checkForImportDependency()					

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
		
