from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root

cluster: Cluster = Cluster(r"Test folder\cluster2")

# pc1 = cluster.create_computer("szamitogep1", 1000, 8000)
# pc2 = cluster.create_computer("szamitogep2", 700, 4000)
# pc3 = cluster.create_computer("szamitogep3", 2000, 2000)
# pc4 = cluster.create_computer("szamitogep4", 1500, 16000)

cluster.smart_rebalancer.distribute_processes_efficient_packing()
cluster.smart_rebalancer.distribute_processes_speedy()