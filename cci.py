from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter
import sys

root = r".\Thing"
if not len(sys.argv) == 1:
    root = sys.argv[1]

interpreter : CLI_Interpreter = CLI_Interpreter(root)