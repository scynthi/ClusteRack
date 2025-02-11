import os
from os import path as Path
import shlex

from modules.cluster import Cluster
from modules.computer import Computer
from modules.root import Root

class CLI_Interpreter:
    
    def __init__(self):
        
        root : Root = Root(r"./mathew")
        
        root_str : str = (r"mathew")

        self.mode : str = "None"
        
        self.current_cluster : Cluster

        self.current_root : Root = root

        self.current_computer : Computer
        
        self.arguments = []
        
        self.root_commands = {
            "select" : {
                "root" : (self.select, "Root", ),
                "cluster" : {},
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
        self.cluster_commands = {
            "select" : {
                "root" : (self.select, "Root", ),
                "cluster" : {},
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, ),
            "rename_computer" : {},
            "create_computer" : ()
            
        }
        
        self.computer_commands = {
            "select" : {
                "root" : (self.select, "Root", ),
                "cluster" : {},
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
        self.noMode_commands = {
            "select" : {
                "root" : (self.select, "Root", ),
                "cluster" : {},
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
        clusters = root.clusters
        
        for item in clusters.keys():
            
            self.cluster_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
            self.noMode_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
            self.computer_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
            self.root_commands["select"]["cluster"].update({f"{item}" :(self.select, "Cluster", clusters[f"{item}"])})
        
        self.take_input()
                
                
    def take_input(self):
        
        command = input(f"{self.mode}>").lower()
        
        self.convert_input(command)
        
    
    def convert_input(self, command):
        
        shlashed_command = shlex.split(command)
        
        self.shlashed_command = shlashed_command
        
        current_step = {}
        
        match self.mode:
            
            case "Root":
                
                current_step, arguments, success = self.cicle_through_commands(self.root_commands, shlashed_command)
                    
            case "Cluster":
                
                try:

                    current_step, arguments, success = self.cicle_through_commands(self.cluster_commands, shlashed_command)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input()
                
            case "Computer":
                
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
        
            
    def select(self, mode, current):
        
        self.mode = mode
        
        self.current_cluster = current
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        
        self.take_input()

    def update_dicts(self):
        
        if self.current_cluster:
        
            computers = self.current_cluster.computers
                
            for item in computers.keys():
                
                self.cluster_commands["rename_computer"].update({f"{item}" : (self.current_cluster.rename_computer, f"{item}")})
                
        if self.current_root:
            
            clusters = self.current_root.clusters
            
            for item in clusters.keys():
                
                self.cluster_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
                self.noMode_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
                self.computer_commands["select"]["cluster"].update({f"{item}" : (self.select, "Cluster", clusters[f"{item}"])})
                self.root_commands["select"]["cluster"].update({f"{item}" :(self.select, "Cluster", clusters[f"{item}"])})
                
            self.cluster_commands["create_computer"] = (self.current_cluster.create_computer, )
        
    
    def exit(self):
        
        print("Bye Bye")
        quit()
        
    def cicle_through_commands(self, command_dict, shlashed_command):
        
        current_step : dict = command_dict

        arguments = []
        
        try:
                
            for item in shlashed_command:
                
                if item == "?":
                            
                    keys = current_step.keys()
                            
                    current_step = ""
                            
                    for coms in keys:
                                
                        current_step += coms + "\n"
                                
                    return current_step, "", True

                if isinstance(current_step, dict) and item not in current_step.keys():

                    for keys in current_step.keys():

                        if item in keys:

                            return f"Did you mean {keys}?", "", False
                        
                    return f"Command not found", "", False
                        
                if isinstance(current_step, dict):
                
                    current_step = current_step[item]

                elif  current_step:

                    arguments.append(item)
            
            if not isinstance(current_step, dict):

                return current_step, arguments, True
            
            else:
                
                current_step = "That is not a full command"
                
                return current_step, "", False
        
        except Exception as e:
            
            print("Something failed", e)
       

"""
                current funcs or sum:
                case "cd":
                    
                    self.current_cluster = Path.join(root_str, command[1])
                
                case "rename":
                    
                    if len(command) != 3:
                        
                        return "Brother you have to give it 2 arguments"
                    
                    Cluster(self.current_cluster).rename_computer(command[1], command[2])
                    
                case "create":
                    
                    if len(command) != 4:
                        
                        return "Brother you have to give it 4 arguments"
                    
                    Cluster(self.current_cluster).create_computer(command[1], int(command[2]), int(command[3]))
                    
                case "exit":
                    
                    break   
"""


"""
TODO
Explanation : 

"""
        