#Author: Arko Basu [ HGST Inc.]
"""Main entry point"""

from .main import ImportXMLSampleSource, CreateWorkFiles, processSoftwarePackage
from .procSoftPack import processSoftwarePackage
from .dynamicMapping import processSoftwarePackageXMLs

ImportXMLSampleSource()
