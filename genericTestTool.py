#!/usr/local/bin python3
#Author: Arko Basu
#Date  : 07212015
#Copyright: HGST Inc.
#Description: Generic Automated Tool

from toolBase import ImportXMLSampleSource, CreateWorkFiles
import argparse
import sys
import os
import time

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Generic Automated System test tool")
	parser.add_argument('-d','--dataSource', dest='XMLFileName', help='absolute path for the sample XML data source. If this is not provided, the System looks for XML sample source in its deafult workFiles directory to find the available already imported sources.')
	args = parser.parse_args()
	xmlDataSource = args.XMLFileName

	if xmlDataSource is None:
		print("Going into sample directory folder.")		
		#Go to workFiles/CompiledXMLSources
	else:
		File = ImportXMLSampleSource(xmlDataSource)
		print("Software Package detected in sample XML Source: " + File.root.tag)
		CreateWorkFiles(File.root)
