from modules.root import Root
from modules.cluster import Cluster
from modules.computer import Computer

# root : Root = Root(r".\Test folder")
# cluster : Cluster = root.clusters.get("cluster0")

# test = [[0,1], [0,1,3], [",22"]]

# for row, items in enumerate(test):
#     for item in items:
#         print(f"Row: {row}, Item: {items.index(item)}")


test2 = {0: [0,1], 1: [0,1,3], 2: [",22"]}

for row in test2:
    for item in test2[row]:
        print(f"Row: {row}, Item: {test2[row].index(item)}")
