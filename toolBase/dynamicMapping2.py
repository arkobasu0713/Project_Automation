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

	"""This function processes the tree extracted from the command script to modify the behaviour of command arguments with "NA" parametervalues.
	Returns the modified tree structure."""

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
						UTIL.printDynamicMappingTechnique()
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

#	"""This function processes the tree extracted from the command script to modify the behaviour of command arguments with "NONE" parametervalues.
#	Returns the modified tree structure."""

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
					modTree.addValues(index,manualEntry)
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

#	"""This function processes a tree extracted from a command script to add any additional parameter values to any of the command arguments at the discretion of the user/tester.
#	Returns the modified tree structure."""

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

#	"""This function facilitates the user to map multiple dependencies of one command argument to any(one or more) command arguments found inside a script.
#	Returns the modified tree structure."""

	add = 'Y'
	while add == 'Y':
		modTree = modifyTree(treeForCommand.commandTree, treeForCommand.listOfCommandArg)
		try:
			add = (input("Do you wish to define multiple dependency in one go?(y/n) : ")).upper()
			if add == 'Y':
				UTIL.printArgsBasedOnIndex(treeForCommand.listOfCommandArg, list(range(len(treeForCommand.listOfCommandArg))))
				UTIL.printDynamicMappingTechnique()
				index = int(input("Select the serial from the above list that you wish to define multiple dependency for: "))
				addTo = [int(i) for i in ((input("Chose from the above list of arguments that you wish to add the command argument " + treeForCommand.listOfCommandArg[index].text + " as dependant argument.(PS, you can add multiple arguments by separating them by a semicolon): ")).split(';'))]
				for singleAddToIndex in addTo:
					pas = [index]
					choice = input(str(treeForCommand.root[index].text) + " (M)andatory/(O)ptional dependant argument to " + str(treeForCommand.root[singleAddToIndex].text) + " ").upper()
					if choice == 'M':
						UTIL.printDynamicMappingTechnique()
						modTree.modifyAdditionalMandatoryGrandChild(singleAddToIndex,pas)
					elif choice == 'O':
						UTIL.printDynamicMappingTechnique()
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

#	"""This function gives a final round of user choice to modify/add behaviours of any command argument found inside the script before exiting the dynamic mapping procedure.
#	Returns the modified tree structure."""

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
						UTIL.printDynamicMappingTechnique()
						depArg = (input("Select the commands that go along with " + treeForCommand.listOfCommandArg[index].text + " as mandatory additional arguments. You can specify multiple commands by separating them with comma(,): ")).split(',')
						depMandArg = [int (i) for i in depArg]
						modTree.modifyAdditionalMandatoryGrandChild(index,depMandArg)
					elif choice == 'O':
						UTIL.printList(treeForCommand.listOfCommandArg)
						UTIL.printDynamicMappingTechnique()
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

#	"""This function processes a command script and facilitates all kinds of dynamic mappings inside the script. Based on the functions
#	it modifies the command script(XML) to generate a new script in the same location.
#	Note that this function only creates a modified file once all the corresponding sub-methods have run successfully and there was no exception thrown."""


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
	
	

	os.remove(commandScript)
	treeForCommand.commandTree.write(commandScript)
	
def defineExportBehaviour(commandIndexOf,commandIndexTo, exportCommand, dictionaryOfCommandsScriptAbsolutePath):

#	"""This function defines the export behaviour of a single command to multiple commands found inside the software package directory in one go.
#	This function is done in order to reduce the redundancy of defining export/import behaviour of multiple command arguments in one go."""

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

			if treeForCommand.root[indvAdd].find('importsFrom') is None:
				newNode = ET.SubElement(treeForCommand.root[indvAdd], 'importsFrom')
				newNode.text = dictionaryOfCommandsScriptAbsolutePath[commandIndexOf]
			else:
				print("Modifying already existing import tag.")
				(treeForCommand.root[indvAdd].find('importsFrom')).text = commandName

		os.remove(dictionaryOfCommandsScriptAbsolutePath[eachIndexOfCommandScript])
		treeForCommand.commandTree.write(dictionaryOfCommandsScriptAbsolutePath[eachIndexOfCommandScript])



class modifyTree():

#	"""This is a class where the argument is a Tree.
#	The submethods of this class are for the modification of the structure of the tree as per the fucntionalities described in the comment section
#	of each of the submethods."""

	def __init__(self,tree, commandArgList):
		self.tree = tree
		self.root = self.tree.getroot()
		self.listOfCommandArg = commandArgList
		self.grandChildMandTag = 'additionalMandDependantArgument'
		self.commandTag = 'command'
		self.grandChildOptTag = 'additionalOptDependantArgument'
		self.importsFromTag = 'importsFrom'

	def modifyAdditionalMandatoryGrandChild(self,modifyCommandArg, depMandCommand):
	
#	"""This submethod creates additional mandatory argument child in the parameter on being called. It appends the arguments in case there is already one existing."""

		text = ''
		for i in depMandCommand:
			text = text + self.listOfCommandArg[i].text + ';'
		text = text.rstrip(';')
					
		if self.root[modifyCommandArg].find(self.grandChildMandTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildMandTag)
			childNode = ET.SubElement(newNode,self.commandTag)
			childNode.text = text
		else:
			childNode = ET.SubElement(self.root[modifyCommandArg].find(self.grandChildMandTag),self.commandTag)
			childNode.text = text
	
				
	def modifyAdditionalOptionalGrandChild(self,modifyCommandArg, depOptCommand):

#	"""This submethod creates additional optional argument child in the parameter on being called. It appends the arguments in case there is already one existing."""
		text = ''
		for i in depOptCommand:
			text = text + self.listOfCommandArg[i].text + ';'
		text = text.rstrip(';')
		if self.root[modifyCommandArg].find(self.grandChildOptTag) is None:
			newNode = ET.SubElement(self.root[modifyCommandArg],self.grandChildOptTag)
			childNode = ET.SubElement(newNode,self.commandTag)
			childNode.text = text
		else:
			childNode = ET.SubElement(self.root[modifyCommandArg].find(self.grandChildOptTag),self.commandTag)
			childNode.text = text

	def modifyManualArgument(self, index, manualEntry):
#	"""This submethod adds a manual entry of parameter values to the parameters."""
		for commandArgVal in self.root[index].iter('parametervalues'):
			commandArgVal.text = manualEntry

	def modifyImportArgument(self,index,commandName):
#	"""This submethod adds the absolute path of the script that needs to be run from which the data of parameter values for the parameter name is to be extacted.
#	It changes the script path in case there is already an existing one."""
	#TODO: add attributes so as to extract dynamic data as mentioned by the user other than the parameter name

		if self.root[index].find(self.importsFromTag) is None:
			newNode = ET.SubElement(self.root[index], self.importsFromTag)
			newNode.text = commandName
		else:
			print("Modifying already existing import tag.")
			(self.root[index].find(self.importsFromTag)).text = commandName

	def addValues(self,index,addValue):
#	"""This method adds new parameter values/appends to existing values."""
		for commandArg in self.root[index].iter('parametervalues'):
			if commandArg.text == 'None':
				commandArg.text = addValue
			else:
				commandArg.text = commandArg.text + ';' + addValue


			

class command():
#	"""This is a class where the command script is provided as an argument, which is then parsed into an XML structured tree.
#	This funtion has several sub-methods which are elaborately explained in each case."""
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
#	"""This submethod retrieves all the parameters under a command script and pushes them on to a list"""
		for commandArg in self.root:
			self.listOfCommandArg.append(commandArg)

	def getCommandArgumentsValues(self):
#	"""This submethod retrieves all the paremeter values in each of the parameters found in the list build from the above method"""
		for commandArg in self.listOfCommandArg:
			for commandArgVal in commandArg.iter('parametervalues'):
				self.listOfCommandArgValues.append(commandArgVal)
				break

	def printCommandName(self):
#	"""This method simply prints the command for which the script is being processed."""
		print("Command: " + str(self.command))
		
	def checkForNAValues(self):
#	"""This submethod looks for parameter values of NA which signifies that the command argument doesn't take any values."""
		for indVal in range(len(self.listOfCommandArgValues)):
			if (self.listOfCommandArgValues[indVal].text) == 'NA':
				self.listOfIndexOfCommandsWithNAValues.append(indVal)

	def checkForNoArgValues(self):
#	"""This submethid looks for parameter values of None which signifies that the commang argument had no parameter values inside the script."""
		for indVal in range(len(self.listOfCommandArgValues)):
			if (self.listOfCommandArgValues[indVal].text) == 'None':
				self.listOfIndexOfCommandsWithNoneValue.append(indVal)
				self.dictOfCommandImportArg[self.listOfCommandArg[indVal].text] = self.listOfCommandArgValues[indVal].attrib

class processSoftwarePackageXMLs(object):

#	"""This is the entry point of the program where the dynamic mapping module of scripts discovered under the software package is run for.
#	This function allows the user to indvidually modify each command XML script, or define multiple dependencies in one go. However the multiple dependencies
#	module is far more losely developed for defining only single dependencies like exporting data from-to. whereas the single command script mapping procedure is
#	much more elaborate and extends from capabilities of adding extra parameter values, defining import data from foreign scripts, to adding dependant arguments(mandatory/optional)"""

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
					defineBehaviourOfCommand(self.dictionaryOfCommandsScriptAbsolutePath[commandIndexOf], self.fileDictionary, self.dictionaryOfCommandsScriptAbsolutePath)
	
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
		
