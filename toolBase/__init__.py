#Author: Arko Basu [ HGST Inc.]
import os
import sys

ext = os.path.join(os.path.dirname(__file__), '..', 'externals')
six = os.path.join(ext, 'six')

sys.path.insert(0, os.path.abspath(ext))
sys.path.append(six)

from .main import ImportXMLSampleSource, CreateWorkFiles
from .procSoftPack import processSoftwarePackage
from .dynamicMapping import processSoftwarePackageXMLs
from .dynamicMapping2 import processSoftwarePackageXMLs
