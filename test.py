from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r".\Test folder", None)
cluster : Cluster = root.clusters["cluster0"]


"""


-- Make sure no negativs in .klazter file


Root
Create cluster                 D
Delete cluster (try, force)    D
Edit cluster name              D
Move computer between clusters 
Move program between clusters  
Cleanup root                   D

Cluster
Create computer            D
Del computer (try, force)  D
Edit computer resources    D
Rename computer            D
Set default rebalance algo D
Run rebalance              D
Cleanup cluster            D

>>(Programok)
     Start program             D
     Stop program              D
     Kill program              D 
     Edit program              D
     Rename program            D

     >>(Program instancek)
         Add prog. instance           D
         Edit prog. instance status   D
         Kill prog. instance          D
         Change prog. instance id     D

Computer:
Cleanup computer D

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