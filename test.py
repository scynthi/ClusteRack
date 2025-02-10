from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r"./Test folder")

cluster1 : Cluster = root.clusters["cluster1"]

# root.relocate_process("chrome", "cluster1", "cluster2")

# Just write test code here
# I cleaned it cause we dont use the commented stuff anyway