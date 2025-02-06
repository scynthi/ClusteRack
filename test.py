from modules.computer import Computer
from modules.cluster import Cluster
from root import Root

root : Root = Root(r".\Test folder")
root.relocate_process("shit-0", "cluster0", "szamitogep1", "cluster3", "computer1")

# pc : Computer = Computer(r"Test folder\cluster3\computer3")
# pc.start_process("shit-0", True, 100, 100)