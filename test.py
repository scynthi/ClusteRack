from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root

root : Root = Root(r".\Test folder")
cluster : Cluster = root.create_cluster("klaszter2")

pc1 = cluster.create_computer("szamitogep1", 1000, 8000)
pc2 = cluster.create_computer("szamitogep2", 700, 4000)
pc3 = cluster.create_computer("szamitogep3", 2000, 2000)
pc4 = cluster.create_computer("szamitogep4", 1500, 16000)

cluster.rename_cluster("cluster2")

cluster.force_delete_computer("szamitogep4")

