from modules.computer import Computer
from cluster import Cluster

cluster = Cluster(r"C:\Github\ClusteRack\Test folder\cluster0")


for name in cluster.computers:
    print(cluster.computers[name])
