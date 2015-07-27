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
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Directory for software package, " + softwarePackageName + " created at " + dirName)
	else:
		print("Directory for software package already exists.")
	return dirName

def GenerateScriptForCommandNameInSoftwarePackageFolder(dirName,commandName):
	fileName = commandName + ".xml"
	filePath = os.path.join(dirName,fileName)
	file = open(filePath, 'wb')
	print("File " + filePath +" for command, " + commandName +" created")
	return file


def ProcessElement(element,dirName):
	for elementContent in element:
		tag = elementContent.tag
		text = elementContent.text
		if 'commandName' in tag:
			fileCreated = GenerateScriptForCommandNameInSoftwarePackageFolder(dirName,text)
			parent = ET.Element(text)
		elif 'param' in tag:
			if 'Value' not in tag and text is not None:
				paramValueTag = tag + "Value"
				child = ET.SubElement(parent,text)
			elif paramValueTag in tag:
				if text is not None:
					if 'NA' in text :
						#dependency mapping
						grandChild = ET.SubElement(child,"NA")
					else:
						grandChild = ET.SubElement(child,text)
				else:
					#dependency mapping
					grandchild = ET.SubElement(child,"None")

#	xml = MNDOM.parseString(ET.tostring(parent,'utf-8'))
#	prettyXMLasString = xml.toprettyxml()
	tree = ET.ElementTree(parent)
	tree.write(fileCreated)
#	fileCreated.write(prettyXMLasString)


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
		dirName = CreateDirectoryForSoftwarePackage(self.root.tag)

		num = 0
		for index in range(0,((len(self.root)-1)+1)):
#			for element in self.root[index]:
			ProcessElement(self.root[index], dirName)














