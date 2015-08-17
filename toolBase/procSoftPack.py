#author: Arko Basu[HGST Inc]
import argparse
import os
import sys
import json
import time
import re
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
		

class processCommandScript():
	def __init__(self,fileName):
		self.fileName = fileName
		self.tree = parseXMLScript(self.fileName)
		self.root = self.tree.getroot()
		self.listOfArguments = []
		self.listOfArgumentVal = []
		print("Command Name: " + self.root.text)

	def getArguments(self):
		for commandArg in self.root:
			self.listOfArguments.append(commandArg)

	def getArgumentValues(self):
		for commandArgVal in self.listOfArguments:
			for val in commandArgVal.iter('parametervalues'):
				self.listOfArgumentVal.append(val)
				break

		

class processSoftwarePackage(object):
	"""This is the function which processes the individial XMLs and runs them agains the system specific CLI and logs the output."""
	def __init__(self,softwarePackageName,softwarePackageXMLFolder,logFilePath):
		self.packageName = softwarePackageName
		self.XMLFolder = softwarePackageXMLFolder
		self.logFilePath = logFilePath
		self.files, self.dictionaryOfAbsPathForXMLs = retreiveXMLFilesAndTheirAbsPath(self.XMLFolder)
		
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
			procCommandScrpt = processCommandScript(self.dictionaryOfAbsPathForXMLs[serial])
			procCommandScrpt.getArguments()
			procCommandScrpt.getArgumentValues()
