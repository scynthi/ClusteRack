import os
from os import path as Path
import shlex

from modules.cluster import Cluster
from modules.computer import Computer
from modules.root import Root

class CLI_Interpreter:
    
    def __init__(self):
        
        root : Root = Root(r"./Thing")

        self.mode : str = "None"
        
        self.current_cluster : Cluster = None

        self.current_root : Root = root

        self.current_computer : Computer = None
        
        self.arguments = []
        
        self.root_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            "create_cluster" : {"<cluster name" : {"?algo" : (self.current_root.create_cluster, )}},
            "try_del_cluster" : {},
            "force_del_cluster" : {},
            "relocate_process" : {"<process name" : {}},

            "move_computer" : (self.current_root.move_computer, ),
            "rename_cluster" : {}
        }

        self.cluster_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            "rename_computer" : {},
            "create_computer" : {"<computer name" : ()}
        }
        
        self.computer_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )}
        }
        
        self.noMode_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )}
        }
        
        clusters = root.clusters
        
        for item in clusters.keys():
            
            self.cluster_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.noMode_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.computer_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.root_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            
            self.cluster_commands["select"]["computer"].update({f"{item}" : {}})
            self.noMode_commands["select"]["computer"].update({f"{item}" : {}})
            self.computer_commands["select"]["computer"].update({f"{item}" : {}})
            self.root_commands["select"]["computer"].update({f"{item}" : {}})
                
            for comps in clusters[item].computers:
                
                self.cluster_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.noMode_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.computer_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.root_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
        
        self.take_input()
                
                
    def take_input(self):
        
        command = input(f"{self.mode}>").lower()
        
        self.convert_input(command)
        
    
    def convert_input(self, command):
        
        shlashed_command = shlex.split(command)
        
        shlashed_command.append("?algo")
        
        self.shlashed_command = shlashed_command
        
        current_step = {}
        
        match self.mode:
            
            case "root":
                
                current_step, arguments, success = self.cicle_through_commands(self.root_commands, shlashed_command)
                    
            case "cluster":
                
                try:

                    current_step, arguments, success = self.cicle_through_commands(self.cluster_commands, shlashed_command)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input()
                
            case "computer":
                
                try:

                    current_step, arguments, success = self.cicle_through_commands(self.noMode_commands, shlashed_command)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input()
                
            case _:
                
                try:

                    current_step, arguments, success = self.cicle_through_commands(self.noMode_commands, shlashed_command)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input()
                
        if isinstance(current_step, tuple):
            
            func, *default_args = current_step

            all_args = (*default_args, *arguments)
            
            func(*all_args)
                    
        elif current_step:
                    
            print(current_step)
            
        self.take_input()
        
    def select_root(self, mode):
        
        self.mode = mode
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        
        self.take_input()
        
            
    def select_cluster(self, mode, cluster):
        
        self.mode = mode
        
        self.current_cluster = cluster
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        
        self.take_input()

        
    def select_computer(self, mode, cluster, computer):
        
        self.mode = mode
        
        self.current_computer = computer
        
        self.current_cluster = cluster
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        
        self.take_input()
        

    def update_dicts(self):
        
        print(self.current_cluster)

        clusters = self.current_root.clusters
        
        for item in clusters.keys():
            
            self.cluster_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.noMode_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.computer_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            self.root_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
            
            self.cluster_commands["select"]["computer"].update({f"{item}" : {}})
            self.noMode_commands["select"]["computer"].update({f"{item}" : {}})
            self.computer_commands["select"]["computer"].update({f"{item}" : {}})
            self.root_commands["select"]["computer"].update({f"{item}" : {}})
                
            for comps in clusters[item].computers:
                
                self.cluster_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.noMode_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.computer_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                self.root_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
        
        
        if self.current_cluster:
        
            computers = self.current_cluster.computers
                
            for item in computers.keys():
                
                self.cluster_commands["rename_computer"].update({f"{item}" : (self.current_cluster.rename_computer, )})
                
            for item in clusters.keys():
                
                self.cluster_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, )}})
                self.noMode_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, )}})
                self.computer_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, )}})
                self.root_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, )}})
                
            self.cluster_commands["create_computer"]["<computer name"] = {"?algo" : (self.current_cluster.create_computer, )}
            
            for item in clusters.keys():
                
                for jitem in clusters.keys():
                
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}}})
                
        if self.current_root:
            
            clusters = self.current_root.clusters
            
            for item in clusters.keys():
                
                self.root_commands["try_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.try_delete_cluster, )}})
                self.root_commands["force_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.force_delete_cluster, )}})
                self.root_commands["rename_cluster"].update({f"{item}" : {"?algo" : (self.current_root.rename_cluster, )}})
                
            for item in self.current_root.clusters.keys():
                
                for jitem in self.current_root.clusters.keys():
                
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}}})
                
    
    def exit(self):
        
        print("Bye Bye")
        quit()
        
    def cicle_through_commands(self, command_dict, shlashed_command):

        current_step : dict = command_dict

        arguments = []
        
        skips = 1

        try:
            for item in shlashed_command:
                
                if "non_args" in current_step.keys():
                
                    skips = current_step["non_args"]
                
                temp = False
                
                temp_item = item
                
                bitem = item

                if item == "?":
   
                    keys = current_step.keys()
                            
                    current_step = ""
                         
                    for coms in keys:
                        
                        if coms != "non_args" and coms != "?value":
                        
                            if "<" in coms:
                                
                                current_step += coms[1:] + "\n"
                                
                            else:
                                    
                                current_step += coms + "\n"
                                
                    return current_step, "", True
                
                if item == "non_args" or item == "?value":
                    
                    return "Can't type that bruw", "", False


                if isinstance(current_step, dict) and item not in current_step.keys():
                    
                    for fitem in current_step.keys():
                    
                        if fitem.startswith("<"):
                            
                            temp = True
                            
                            temp_item = fitem
                            
                    if not temp:

                        for keys in current_step.keys():

                            if item in keys:

                                return f"Did you mean {keys}?", "", False
                        
                        return f"Command not found", "", False
                
                if type(current_step[temp_item]) != tuple:
                    
                    if "?value" in current_step[temp_item].keys():
                        
                        bitem = current_step[temp_item]["?value"]
                
                if bitem != "?algo":
                
                    arguments.append(bitem)
                    
                current_step = current_step[temp_item]
                
            arguments = arguments[skips:]
            
            if not isinstance(current_step, dict):

                return current_step, arguments, True
            
            else:
                
                current_step = "That is not a full command"
                
                return current_step, "", False
        
        except Exception as e:
            
            print("Something failed", e)

"""
TODO
Explanation : 

"""
        