from modules.computer import Computer
from modules.cluster import Cluster

cluster = Cluster(r"Test folder\anyad")


for name in cluster.computers:
    pc: Computer = cluster.computers[name]