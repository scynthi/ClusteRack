from modules.computer import Computer
from modules.cluster import Cluster
from root import Root

pc : Computer = Computer(r"Test folder\cluster0\szamitogep4")
pc.start_process("shit", True, 100, 100)
