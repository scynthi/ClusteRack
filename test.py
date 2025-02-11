from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r"./Test folder")
cluster : Cluster = root.create_cluster("test_cluster")

# cluster.create_computer("test", 1000,1000)
# root.relocate_process("", "")
# root.force_delete_cluster("test_cluster")






"""
Featres:
- root :
- create cluster
- try delete cluster
- force delete cluster
- relocate process
- move computer
- rename cluster

- cluster:
- create computer
- try delete computer
- force delete computer
- rename computer
- start process
- kill process
- edit process resources
- rename process

- rebalancer:
- balanced algo
- efficient algo
- fast algo

- computer:
- edit computer resources
- get processes
"""

"""
CLI Commands
- select <root obj>
- select <cluster obj> <cluster name>
- select <computer obj> <cluster name> <computer name>

- Root comms:
- create_cluster <cluster name>
- try_del_cluster <cluster name>
- force_del_cluster <cluster name>
- relocate_process <process name> <origin> <destination>
- move_computer <computer name> <origin> <destination>
- rename_cluster <target name> <new name>

- Cluster comms:
- set_default_rebalance_algo <load_balance (or) best_fit (or) fast>
- run_default_rebalance
- run_rebalance <load_balance (or) best_fit (or) fast>
- create_computer <computer name> <cores> <memory>
- try_del_computer <computer name>
- force_del_computer <computer name>
- rename_computer <target computer> <new name>
- start_process <process name> <status> <req cores> <req memory> <instance count> <date started(optional)>
- kill_process <process name>
- edit_process_resources <process name> <prop to change> <new value>
- rename_process <process name> <new name>


- Computer comms:
- edit_resources <core> <memory>
- get_processes
"""

# Just write test code here
# I cleaned it cause we dont use the commented stuff anyway