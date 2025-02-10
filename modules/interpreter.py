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

        self.current_root : Root

        self.current_computer : Computer
        
        self.arguments = []
        
        self.root_commands = {
            "select" : {
                "root" : (self.select, "Root"),
                "cluster" : (self.select, "Cluster"),
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
        self.cluster_commands = {
            "select" : {
                "root" : (self.select, "Root"),
                "cluster" : (self.select, "Cluster"),
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
            
        }
        
        self.computer_commands = {
            "select" : {
                "root" : (self.select, "Root"),
                "cluster" : (self.select, "Cluster"),
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
        self.noMode_commands = {
            "select" : {
                "root" : (self.select, "Root"),
                "cluster" : (self.select, "Cluster"),
                "computer" : (self.select, "Computer")
            },
            "exit" : (self.exit, )
        }
        
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
                
                current_step = self.cicle_through_commands(self.root_commands, shlashed_command)
                    
            case "Cluster":
                
                current_step = self.cicle_through_commands(self.cluster_commands, shlashed_command)
                
            case "Computer":
                
                current_step = self.cicle_through_commands(self.computer_commands, shlashed_command)
                
            case _:
                
                current_step = self.cicle_through_commands(self.noMode_commands, shlashed_command)
                
        if isinstance(current_step, tuple):
            
            func, *args = current_step
            
            func(*args)
                    
        elif current_step:
                    
            print(current_step)
            
        self.take_input()
        
            
    def select(self, mode):
        
        self.mode = mode
        
        print(f"selected the {mode}")
        
        self.take_input()
        
    
    def exit(self):
        
        print("Bye Bye")
        quit()
        
    def rename(self):
        
        pass
        
        
    def cicle_through_commands(self, command_dict, shlashed_command):
        
        current_step : dict = command_dict
        
        try:
                
            for item in shlashed_command:
                        
                if item == "?":
                            
                    keys = current_step.keys()
                            
                    current_step = ""
                            
                    for coms in keys:
                                
                        current_step += coms + "\n"
                                
                    break
                        
                        
                
                current_step = current_step[item]
                
            return current_step
        
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
        