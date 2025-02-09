from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root

# root : Root = Root(r"./Test folder")

# cluster1 : Cluster = root.create_cluster("cluster1")
# pc1 = cluster1.create_computer("szamitogep1", 1200, 5000)
# pc2 = cluster1.create_computer("szamitogep2", 900, 4000)
# pc3 = cluster1.create_computer("szamitogep3", 1900, 2000)
# pc4 = cluster1.create_computer("szamitogep4", 8000, 6000)

cluster: Cluster = Cluster(r"Test folder\klaszter1")
pc1 = cluster.create_computer("szamitogep1", 1000, 8000)
pc2 = cluster.create_computer("szamitogep2", 700, 4000)
pc3 = cluster.create_computer("szamitogep3", 2000, 2000)
pc4 = cluster.create_computer("szamitogep4", 1500, 16000)

cluster.rebalancer.distribute_processes_speedy()
cluster.rebalancer.distribute_processes_efficient_packing()
cluster.rebalancer.distribute_processes_balanced()