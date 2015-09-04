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
from . import utils as UTIL

def ProcessElement(element,XMLScriptDirectory):

	"""This function processes each of the elements found under the root of the original XML Data source 
	and creates child tags based on the parameters to create separate files and write then in the XML directory"""

	paramTag = 'parameter'
	paramValTag = 'parametervalues'
	for elementContent in element:
		tag = elementContent.tag
		text = elementContent.text
		if 'commandName' in tag:
			fileCreated = UTIL.GenerateScriptForCommandNameInSoftwarePackageFolder(XMLScriptDirectory,text)
			parent = ET.Element(tag)
			parent.text = text
		elif 'param' in tag:
			if 'Value' not in tag and text is not None:
				paramValueTag = tag + "Value"
				child = ET.SubElement(parent,paramTag)
				child.text = text
			elif paramValueTag in tag:
				if text is not None:
					if 'NA' in text :
						#dependency mapping
						grandChild = ET.SubElement(child,paramValTag)
						grandChild.text = "NA"
					else:
						grandChild = ET.SubElement(child,paramValTag)
						grandChild.text = text
				else:
					#dependency mapping
					grandChild = ET.SubElement(child,paramValTag)
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
			print("Processing sample data source: " + self.fileName)
		else:
			print("File location invalid. Please try the absolute filepath of the data source")
		
		self.tree = UTIL.parseXMLScript(self.fileName)
		self.root = self.tree.getroot()

		print("Software Package detected in sample XML Source: " + self.root.tag)
		self.dirName, self.XMLScriptDirectory = UTIL.CreateDirectoryForSoftwarePackage(self.root.tag)
		CreateIndividualFilesForRootElement(self.root, self.XMLScriptDirectory)
		print("At this point, the input data source has been processed and the correspoding individual XML scripts have been generated in " + self.XMLScriptDirectory)
		print("Please verify the XML files in the above mentioned folder.")

def CreateIndividualFilesForRootElement(rootElement,XMLScriptDirectory):
	"""This Function processes the XML tree and creates separate card/XML files for each of the command suits"""
	for index in range((len(rootElement)-1)+1):
		ProcessElement(rootElement[index], XMLScriptDirectory)

		




