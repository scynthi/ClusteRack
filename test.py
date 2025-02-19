from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r".\Test folder", None)


# cluster : Cluster = root.clusters["cluster0"]
cluster1 = root.create_cluster("cluster0")
cluster1.stop_program("chrome")

"""
Root
Create cluster                 D
Delete cluster (try, force)    D
Edit cluster name              D
Move computer between clusters D
Move program between clusters  D
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
         Add prog. instance           D BUG
         Edit prog. instance status   D
         Kill prog. instance          D
         Change prog. instance id     D

Computer:
Cleanup computer D

"""



"""
CLI Commands
- Mode select:
- select <root>      # Selects root mode in the CLI
- select <cluster> <cluster name> # Selects cluster mode in the CLI
- select <computer> <cluster name> <computer name> # Selects cluster mode in the CLI

- Root comms:
- create_cluster <cluster name>                                  (calls root.create_cluster)
- try_del_cluster <cluster name>                                 (calls root.delete_cluster(cluster_name, mode="try"))
- force_del_cluster <cluster name>                               (calls root.delete_cluster(cluster_name, mode="f"))
- relocate_program <program name> <origin> <destination>         #moves programs between clusters
- move_computer <computer name> <origin> <destination>           #moves computers between clusters
- rename_cluster <target name> <new name>                        (calls root.rename_cluster)
- cleanup_root (no arguments needed)                             (calls root.cleanup)

- Cluster comms:
- set_rebalance_algo <0 (or) 1 (or) 2>                                     (calls cluster.set_rebalance_algo)
- run_rebalance                                                            (calls cluster.run_rebalance)
- create_computer <computer name> <cores> <memory>                         (calls cluster.create_computer)
- try_del_computer <computer name>                                         (calls cluster.delete_computer(computer_name, mode="try"))
- force_del_computer <computer name>                                       (calls cluster.delete_computer(computer_name, mode="f"))
- rename_computer <target computer> <new name>                             (calls cluster.rename_computer)
- edit_computer_resources <computer name> <cores> <memory>                 (calls cluster.edit_computer_resources)
- get_cluster_programs                                                     
- get_cluster_instances                                                    

- start_program <program name> <instance count> <req cores> <req memory>   (calls cluster.add_program)
- kill_program <program name>                                              (calls cluster.kill_program)
- stop_program <program name>                                              (calls cluster.stop_program) 
- edit_program_resources <program name> <prop to change> <new value>       (calls cluster.edit_program_resources)
- rename_program <program name> <new name>                                 (calls cluster.rename_program)
 
- add_instance_gen_id <program name>                                       (calls cluster.add_instance)
- add_instance_user_id <program name> <instance_id>                        (calls cluster.add_instance)
- edit_instance_status <instance id> <new status>                          (calls cluster.edit_instance_status)
- kill_instance <instance id>                                              (calls cluster.kill_instance)
- change_instance_id_gen <instance id>                                     (calls cluster.change_instance_id) NOTE: itt a program name (nem kell hasznalni) az azert van ott mert ha nagyon specifikusak akarunk lenni akkor meg lehet adni hogy melyik program instancet akarjuk atnevezni
- change_instance_id_user <instance id> <new instance id>                  (calls cluster.change_instance_id)
- cleanup_cluster                                                          (calls cluster.cleanup)

- Computer comms:
- cleanup_computer                                                         (calls computer.cleanup)

- 

bnf
https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
"""

"""
<command> ::= <mode_select> 
            | <root_command>
            | <cluster_command>
            | <computer_command>

<mode_select> ::= "select" <root> 
                | "select" <cluster> <cluster_name>
                | "select" <computer> <cluster_name> <computer_name>

<root_command> ::= "create_cluster" <cluster_name>
                 | "try_del_cluster" <cluster_name>
                 | "force_del_cluster" <cluster_name>
                 | "relocate_program" <program_name> <origin> <destination>
                 | "move_computer" <computer_name> <origin> <destination>
                 | "rename_cluster" <target_name> <new_name>
                 | "cleanup_root"

<cluster_command> ::= "set_rebalance_algo" <algo_id>
                    | "run_rebalance"
                    | "create_computer" <computer_name> <cores> <memory>
                    | "try_del_computer" <computer_name>
                    | "force_del_computer" <computer_name>
                    | "rename_computer" <target_computer> <new_name>
                    | "edit_computer_resources" <computer_name> <cores> <memory>
                    | "get_cluster_programs"
                    | "get_cluster_instances"
                    | "start_program" <program_name> <instance_count> <req_cores> <req_memory>
                    | "kill_program" <program_name>
                    | "stop_program" <program_name>
                    | "edit_program_resources" <program_name> <prop_to_change> <new_value>
                    | "rename_program" <program_name> <new_name>
                    | "add_instance_gen_id" <program_name>
                    | "add_instance_user_id" <program_name> <instance_id>
                    | "edit_instance_status" <instance_id> <new_status>
                    | "kill_instance" <instance_id>
                    | "change_instance_id_gen" <instance_id>
                    | "change_instance_id_user" <instance_id> <new_instance_id>
                    | "cleanup_cluster"

<computer_command> ::= "cleanup_computer"

<root> ::= "root"
<cluster> ::= "cluster"
<computer> ::= "computer"

<cluster_name> ::= <string>
<computer_name> ::= <string>
<target_name> ::= <string>
<new_name> ::= <string>
<program_name> ::= <string>
<instance_id> ::= <string>
<new_instance_id> ::= <string>
<prop_to_change> ::= <string>
<new_value> ::= <string>
<origin> ::= <string>
<destination> ::= <string>

<cores> ::= <integer>
<memory> ::= <integer>
<instance_count> ::= <integer>
<req_cores> ::= <integer>
<req_memory> ::= <integer>
<algo_id> ::= "0" | "1" | "2"
<new_status> ::= <string>

<string> ::= ? any sequence of non-whitespace characters ?
<integer> ::= ? any sequence of digits ?
"""