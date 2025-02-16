from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

# root : Root = Root(r"./Thing")
# cluster : Cluster = root.clusters.get("test_cluster")

# root.rename_cluster("cluster4", "cluster0")
# cluster1.start_process("jani", False, 100,100,2)
# cluster1.kill_process("jani")

# root.move_computer("test_computer", "test_cluster", "test_cluster1")

# cluster1.rename_process("jani", "internet")
# cluster1.edit_process_resources("internet", "running", True)

# root.relocate_process("internet", "test_cluster1", "test_cluster")s

root : Root = Root(r".\Test folder")
cluster : Cluster = root.clusters["cluster0"]

print("-----------------------------------------------1111111111")
test_cluster = root.create_cluster("test_cluster")
test_cluster.create_computer("test_comp", 1000, 1000)
# test_cluster.delete_computer("test_comp", "f")

print(test_cluster.computers)

print("-----------------------------------------------22222222222222")
root.delete_cluster("test_cluster")
print("-----------------------------------------------3333333333333")

# cluster._load_programs()

# cluster.edit_instance("internet-")
# cluster.edit_computer_resources("computer2", 4000,8000)



# cluster.create_computer("computer1", 2000, 8000)
# cluster.create_computer("computer2", 2000, 8000)

# cluster.reload_cluster()
# cluster.delete_computer("computer2", "f")

# cluster.rename_computer("test_computer", "computer2")

# cluster.edit_computer_resources("computer2", 4000, 4000)

# cluster.run_rebalancer()

"""
Root
Create cluster                 D
Delete cluster (try, force)    
Edit cluster name
Move computer between clusters
Move program between clusters
Cleanup root

Cluster
Create computer D
Del computer (try, force)  D
Edit computer resources    D
Rename computer            D
Set default rebalance algo D
Run rebalance              D
Cleanup cluster 

>>(Programok)
     Start program             D
     Stop program              D
     Kill program              D 
     Edit program
     Restart program
     >>(Program instancek)
         Add prog. instance    
         Edit prog. instance status   D
         Kill prog. instance   D
         Move prog. instance 

Computer:
Cleanup computer D

"""
"""
TODO: Bugs - if we start the cluster with a computer that has 1,1 resources and we try to rebalance to it the instance adding fails but we never put the instance else where -> Update the whole rebalancing algorythm
"""












"""
CLI Commands
- Mode select:
- select <root>
- select <cluster> <cluster name>
- select <computer> <cluster name> <computer name>

- Root comms:
- create_cluster <cluster name>
- try_del_cluster <cluster name>
- force_del_cluster <cluster name>
- relocate_program <program name> <origin> <destination>
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
- start_program <program name> <status> <req cores> <req memory> <instance count> <date started(optional)>
- kill_program <program name>
- edit_program_resources <program name> <prop to change> <new value>
- rename_program <program name> <new name>


- Computer comms:
- edit_resources <core> <memory>
- get_processes - Just gives back a dict of the subprocesses under the computer

bnf
https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form

"""