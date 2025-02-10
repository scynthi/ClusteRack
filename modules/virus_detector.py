import os
import time
from os import path as Path
from modules.computer import Computer
from modules.cluster import Cluster
from colorama import Fore, Style, Back

class VirusDetector:
    def __init__(self):
        pass
        
    

# Virus detection:
# if there is a new file in any of the computer directories that is a valid process file we save its data and check if its it already exist in the active processes
# ( check name and id but not resources )

# if it does just delete it
# if it doesnt ask the user wether to delete it or put it in the processes dict.

# Resort the cluster after this
# ( happens either way )