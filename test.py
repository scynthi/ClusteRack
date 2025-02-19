from modules.computer import Computer
from modules.cluster import Cluster
from modules.root import Root
from modules.interpreter import CLI_Interpreter

root : Root = Root(r".\Test folder", None)


# cluster : Cluster = root.clusters["cluster0"]
cluster1 = root.create_cluster("cluster0")
root.relocate_program("word", "cluster1", "cluster0")

# cluster1.kill_program("testprog2")
# cluster1.delete_computer("computer1", "f")
# cluster1.create_computer("computer1", 1000, 1000)
# cluster1.create_computer("computer2", 1000, 1000)
# cluster1.set_rebalance_algo(0)
# cluster1.run_rebalance()
# cluster1.delete_computer("computer2", "f")
# cluster1.add_program("testprog2", 2, 100,100)




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
- select <root>
- select <cluster> <cluster name>
- select <computer> <cluster name> <computer name>

- Root comms:
- create_cluster <cluster name>                                  (calls root.create_cluster)
- try_del_cluster <cluster name>                                 (calls root.delete_cluster(cluster_name, mode="try"))
- force_del_cluster <cluster name>                               (calls root.delete_cluster(cluster_name, mode="f"))
- relocate_program <program name> <origin> <destination>         NOT DONE YET
- move_computer <computer name> <origin> <destination>           NOT DONE YET
- rename_cluster <target name> <new name>                        (calls root.rename_cluster)
- cleanup_root (no arguments needed)                             (calls root.cleanup)

- Cluster comms:
- set_rebalance_algo <0 (or) 1 (or) 2>                                     (calls cluster.set_rebalance_algo)  the numbers are ints they choose from this list ["load_balance", "best_fit", "fast"]
- run_rebalance                                                            (calls cluster.run_rebalance)
- create_computer <computer name> <cores> <memory>                         (calls cluster.create_computer)
- try_del_computer <computer name>                                         (calls cluster.delete_computer(computer_name, mode="try"))
- force_del_computer <computer name>                                       (calls cluster.delete_computer(computer_name, mode="f"))
- rename_computer <target computer> <new name>                             (calls cluster.rename_computer)
- edit_computer_resources <computer name> <cores> <memory>                 (calls cluster.edit_computer_resources)
- get_cluster_programs                                                     NAGYON LOW PRIO csak kiprinteli a neveit a programoknak a clusteren
- get_cluster_instances                                                    NAGYON LOW PRIO csak kiprinteli a programokat es mellejuk veluk egysorba az instance-iket pl.: word asd123 asd124 

- start_program <program name> <instance count> <req cores> <req memory>   (calls cluster.add_program) NOTE:itt van meg uccso arg a functionok vegen altalaban a reload nem kell foglalkoznod vele
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
- cleanup_computer                                             (calls computer.cleanup)

bnf
https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
"""