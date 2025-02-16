from modules.root import Root
from modules.cluster import Cluster
from modules.computer import Computer

root : Root = Root(r".\Test folder")
cluster : Cluster = root.create_cluster("test_cluster")
cluster.create_computer("petigep", 6969, 420420)

root.delete_cluster("test_cluster")


