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
        
        self.current_cluster : Cluster
        
        while True:
        
            command = input("Enter da command: ")
            
            try:
                
                command = shlex.split(command)
                
            except Exception as e:
                
                print(f"Baj van borger {e}") 
            
            self.command = command
            
            match command[0]:
                
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
TODO
Explanation : 

"""
        