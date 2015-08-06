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

def processXML(absPathForXMLFile,logFilePath):
	tree = ETProc.parse(absPathForXMLFile)
	command = tree.getroot()
	print("Command: " + command.tag)
	for arguments in command:
		print(arguments.tag + ',' + arguments.text)
		for argValues in arguments:
			if str(argValues.tag) == 'None':
				yOn = input("Parameter " + arguments.text + " has no values in the source. Would you like to modify the data source and put in some value for it? (y/n): ")
				if yOn.upper() == 'Y':
					value = input("Input the value here: ")
					#modify the source XML file to add this value
			else:
				print(argValues.tag + ',' +argValues.text)

class processSoftwarePackage(object):
	"""This is the function which processes the individial XMLs and runs them agains the system specific CLI and logs the output.
	It also has the utility of mapping dependencies. creating multiple tupples of parameters that are passed in to the command's run, 
	and also modify them dynamically"""
	def __init__(self,softwarePackageFolder,LogFilePath,rootFileElementTag):
		self.rootElementTag = rootFileElementTag
		self.packageFolder = softwarePackageFolder
		self.logFilePath = LogFilePath
		xmlPathInsideSoftwarePackage = os.path.join(self.packageFolder,'XMLScripts')
		dictionaryOfAbsPathForXMLs = {}
		print("Command Scripts found inside the package folder: ")
		for dirpath, dirnames, filenames in os.walk(xmlPathInsideSoftwarePackage):
			index=1
			for files in filenames:
				if files.endswith(".xml"):
					print(str(index) + ". " + files)
					dictionaryOfAbsPathForXMLs[index] = os.path.join(xmlPathInsideSoftwarePackage,files)
					index = index + 1
		
		serialNumCommand = int(input("Please type in the serial number of the command that you'd wish to run: "))
		processXML(dictionaryOfAbsPathForXMLs[serialNumCommand],self.logFilePath)

