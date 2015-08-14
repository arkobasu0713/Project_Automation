#author: Arko Basu[HGST Inc]
import argparse
import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as MNDOM

def ProcessXMLTree(readXMLFile):
	"""This Function processes the Input XML source and generates a list with all the commands and their corresponding argument values"""

	#Import the XML Source File
	tree = ET.parse(readXMLFile)
	if tree is not None:
		print("Import Successful.")
	else:
		print("Malicious corrupted XML File. Please generate the XML file again")

	root = tree.getroot()
	return root

def CreateDirectoryForSoftwarePackage(softwarePackageName):
	"""This function creates a folder for software package imported through data source in workFiles/processedFiles"""
	dirName = os.path.join(os.path.dirname(__file__), '..', 'workFiles', 'processedFiles',softwarePackageName)
	XMLScriptDirectory = ''
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Directory for software package, " + softwarePackageName + " created at " + dirName)
		XMLScriptDirectory = os.path.join(dirName,'OriginalXMLScripts')
		os.mkdir(XMLScriptDirectory)
		print("Directory for XML scripts for corresponding software package, generated at: " + XMLScriptDirectory)
	else:
		print("Directory for software package already exists.")
	return dirName, XMLScriptDirectory

def GenerateScriptForCommandNameInSoftwarePackageFolder(XMLScriptDirectory,commandName):
	fileName = commandName + ".xml"
	filePath = os.path.join(XMLScriptDirectory,fileName)
	file = open(filePath, 'wb')
	print("File " + filePath +" for command, " + commandName +" created")
	return file


def ProcessElement(element,dirName,XMLScriptDirectory):
	childTag = 'parameter'
	grandChildtag = 'parametervalues'
	for elementContent in element:
		tag = elementContent.tag
		text = elementContent.text
		if 'commandName' in tag:
			fileCreated = GenerateScriptForCommandNameInSoftwarePackageFolder(XMLScriptDirectory,text)
			parent = ET.Element(tag)
			parent.text = text
		elif 'param' in tag:
			if 'Value' not in tag and text is not None:
				paramValueTag = tag + "Value"
				child = ET.SubElement(parent,childTag)
				child.text = text
			elif paramValueTag in tag:
				if text is not None:
					if 'NA' in text :
						#dependency mapping
						grandChild = ET.SubElement(child,grandChildtag)
						grandChild.text = "NA"
					else:
						grandChild = ET.SubElement(child,grandChildtag)
						grandChild.text = text
				else:
					#dependency mapping
					grandChild = ET.SubElement(child,grandChildtag)
					grandChild.text = "None"

	tree = ET.ElementTree(parent)
	tree.write(fileCreated)

class ImportXMLSampleSource(object):
	"""This is where the sample XML data source is consumed.
	Once that is done, it is compiled into separate card XML files for later use and stored 
	in a sample work directory build under the workFiles. """
	root = None
	def __init__(self,xmlDataSource):
		self.fileName = str(xmlDataSource)

		print("The XML datasource being used for the operation: " + str(self.fileName))

		#Validate if file exists
		if os.path.isfile(self.fileName):
			print("File exists at specified location.")
		else:
			print("File location invalid. Please try the absolute filepath of the data source")
		
		self.root = ProcessXMLTree(self.fileName)
		

class CreateWorkFiles(object):
	"""This Function processes the XML tree and creates separate card/XML files for each of the command suits"""
	def __init__(self, root):
		self.root = root
		self.dirName, self.XMLScriptDirectory = CreateDirectoryForSoftwarePackage(self.root.tag)

		num = 0
		for index in range(0,((len(self.root)-1)+1)):
			ProcessElement(self.root[index], self.dirName, self.XMLScriptDirectory)

		



