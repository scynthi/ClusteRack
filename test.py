from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r"./Test folder")
cluster : Cluster = root.clusters.get("test_cluster")
cluster1 : Cluster = root.clusters.get("test_cluster1")


pc : Computer = cluster1.computers.get("test_computer")


"""
Featres:
- root :
- create cluster D
- try delete cluster D
- force delete cluster D
- relocate process D
- move computer D
- rename cluster D

- cluster:
- create computer D
- try delete computer D
- force delete computer D
- rename computer D
- start process D
- kill process D
- edit process resources D
- rename process D

- rebalancer:
- balanced algo D
- efficient algo D
- fast algo D

- computer:
- edit computer resources TODO : FIX THIS
- get processes D
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
