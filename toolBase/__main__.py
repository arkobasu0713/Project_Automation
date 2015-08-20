#Author: Arko Basu [ HGST Inc.]
"""Main entry point"""

from .main import ImportXMLSampleSource, processSoftwarePackage
from .procSoftPack import processSoftwarePackage
from .dynamicMapping2 import processSoftwarePackageXMLs
import . utils as UTIL

ImportXMLSampleSource()
