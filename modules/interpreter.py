import os
from os import path as Path
import shlex

from modules.cluster import Cluster
from modules.computer import Computer
from modules.root import Root
import msvcrt
import sys

class CLI_Interpreter:
    
    def __init__(self):
        
        root : Root = Root(r"./Thing")
        
        self.folder = r"./sutoandar"
        
        self.run = False

        self.mode : str = "None"
        
        self.current_cluster : Cluster = None

        self.current_root : Root = root
        
        self.previous_commands = []

        self.current_computer : Computer = None
        
        self.arguments = []
        
        self.root_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            "create_cluster" : {"<cluster name" : {"?algo" : (self.current_root.create_cluster, )}},
            "try_del_cluster" : {},
            "force_del_cluster" : {},
            "relocate_process" : {"<process name" : {}},
            "move_computer" : (self.current_root.move_computer, ),
            "rename_cluster" : {},
            "run" : {"<file name" : {"?algo" : (self.read_file, )}}
        }

        self.cluster_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            # "set_default_rebalance_algo" : {"load_balance" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}, "best_fit" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}, "fast" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}},
            # "run_default_rebalance" : {"?algo" : (self.current_cluster.run_default_rebalance_algo, )},
            # "run_rebalance" : {"?algo" : (self.current_cluster.run_default_rebalance_algo, )},
            "create_computer" : {"<computer name" : ()},
            "try_del_computer" : {},
            "force_del_computer" : {},
            "rename_computer" : {},
            # "start_process" : {"<process name" : {"<running" : {"<cpu_req" : {"<ram_req" : {"<instance_count" : {"<date_started" : {"?algo" : (self.current_cluster.start_process, )}}}}}}},
            "kill_process" : {},
            "edit_process_resources" : {},
            "rename_process" : {},
            "run" : {"<file name" : {"?algo" : (self.read_file, )}}
        }
        
        self.computer_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            "run" : {"<file name" : {"?algo" : (self.read_file, )}},
            "edit_resources" : {},
            "get_processes" : {"?algo" : ()}
        }
        
        self.noMode_commands = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1}
            },
            "exit" : {"?algo" : (self.exit, )},
            "run" : {"<file name" : {"?algo" : (self.read_file, )}}
        }
        
        clusters = root.clusters
        
        if clusters:
        
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
        
        self.take_input("")
                
                
    def take_input(self, default_text):
        
        match self.mode.lower():
            
            case "computer":
                
                prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>{self.current_computer.name.capitalize()}"
                
            case "cluster":
                
                prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}"
                
            case "root":
                
                prompt = f"{self.current_root.name.capitalize()}"
                
            case _:
                
                prompt = "None"

        user_input = f"{default_text}"
        if len(user_input) > 0:
            cursor_pos = len(user_input)
        else:
            cursor_pos = 0
        sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
        sys.stdout.flush()
        
        prev_com_index = -1
        
        
        while True:
            
            key_event = msvcrt.getch()
                
            if key_event == b"\t":
                
                current_step, arguments, success, user_input = self.cicle_through_commands(self.root_commands, shlex.split(user_input), user_input, True)
                cursor_pos = len(user_input)
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                continue  # Keep waiting for user input
            
            elif key_event == b'\x00' or key_event == b'\xe0':
                
                ch2 = msvcrt.getch()
                
                if ch2 == b'\x4b':  # Left arrow key
                    if cursor_pos > 0:
                        cursor_pos -= 1
                        sys.stdout.write("\r")
                        sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                        sys.stdout.write("\033[1D")
                        sys.stdout.flush()
                elif ch2 == b'\x4d':  # Right arrow key
                    if cursor_pos < len(user_input):
                        cursor_pos += 1
                        sys.stdout.write("\r")
                        sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                        sys.stdout.write("\033[1C")
                        sys.stdout.flush()
                        
                elif ch2 == b'\x48':  # Up arrow
                    
                    if prev_com_index < len(self.previous_commands) - 1:
                        
                        prev_com_index += 1

                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)
                        
                    sys.stdout.write("\r")
                    sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()

                elif ch2 == b'\x50':  # Down arrow
                    
                    if prev_com_index > 0:
                        
                        prev_com_index -= 1
    
                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)
                        
                    sys.stdout.write("\r")
                    sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
            
            elif key_event == b"\r":
                
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input}")
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                print()
                if "\x00" in user_input:
                    
                    user_input = user_input.replace("\x00", "")
                self.previous_commands.insert(0, user_input)
                break  # Stop input
            
            elif key_event == b"\x08":
                
                if cursor_pos > 0:
                    user_input = user_input[:cursor_pos-1] + user_input[cursor_pos:]
                    cursor_pos -= 1
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                continue
            
            elif key_event == b" ":
                
                user_input += " "
                cursor_pos += 1
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                continue
            
            else:

                user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                cursor_pos += 1
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                continue
        
        self.convert_input(user_input)
        
    
    def read_file(self, file_name):
        
        file = file_name + ".txt"
        
        file = Path.join(self.folder, file)
        
        with open(file, "r") as f:
            
            temp_commands = f.readlines()
            f.close()
        
        commands = []
            
        for coms in temp_commands:
            
            commands.append(coms.replace("\n", ""))
            
        print(commands)
        
        self.run = True
            
        for item in commands:
            
            match self.mode.lower():
            
                case "computer":
                    
                    prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>{self.current_computer.name.capitalize()}>"
                    
                case "cluster":
                    
                    prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>"
                    
                case "root":
                    
                    prompt = f"{self.current_root.name.capitalize()}>"
                    
                case _:
                    
                    prompt = "None>"
            
            print(f"{prompt}{item}")
            self.convert_input(item)
            
        self.run = False
            

    
    def convert_input(self, command):
        
        shlashed_command = shlex.split(command)
        
        shlashed_command.append("?algo")
        
        self.shlashed_command = shlashed_command
        
        current_step = {}
        
        match self.mode:
            
            case "root":
                
                current_step, arguments, success, default_text = self.cicle_through_commands(self.root_commands, shlashed_command, command, False)
                    
            case "cluster":
                
                try:

                    current_step, arguments, success, default_text = self.cicle_through_commands(self.cluster_commands, shlashed_command, command, False)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input("")
                
            case "computer":
                
                try:

                    current_step, arguments, success, default_text = self.cicle_through_commands(self.noMode_commands, shlashed_command, command, False)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input("")
                
            case _:
                
                try:

                    current_step, arguments, success, default_text = self.cicle_through_commands(self.noMode_commands, shlashed_command, command, False)

                except Exception as e:

                    print(f"Something went wrong {e}")
                    self.take_input("")
        
                
        if isinstance(current_step, tuple):
            
            func, *default_args = current_step

            all_args = (*default_args, *arguments)
            
            returning = func(*all_args)
            
            if returning:
            
                print(returning)
                    
        elif current_step:
                    
            print(current_step)
            
        if not self.run:

            self.take_input(f"{default_text}")
        
    def select_root(self, mode):
        
        self.mode = mode
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        
            
    def select_cluster(self, mode, cluster):
        
        self.mode = mode
        
        self.current_cluster = cluster
        
        self.update_dicts()
   
        print(f"selected the {mode}")

        
    def select_computer(self, mode, cluster, computer):
        
        self.mode = mode
        
        self.current_computer = computer
        
        self.current_cluster = cluster
        
        self.update_dicts()
   
        print(f"selected the {mode}")
        

    def update_dicts(self):

        clusters = self.current_root.clusters
        
        if self.current_computer:
            
            self.computer_commands["get_processes"]["?algo"] = (self.current_computer.get_processes, )
            
        if clusters:
        
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
                
                # self.cluster_commands["rename_computer"].update({f"{item}" : {"?algo" : (self.current_cluster.rename_computer, )}})
                # self.cluster_commands["try_del_computer"].update({f"{item}" : {"?algo" : (self.current_cluster.try_delete_computer, )}})
                # self.cluster_commands["force_del_computer"].update({f"{item}" : {"?algo" : (self.current_cluster.force_delete_computer, )}})
                pass
                
            for item in clusters.keys():
                
                self.cluster_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.noMode_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.computer_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.root_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                
                
            
            # for item in self.current_cluster.processes.keys():
                
            #     self.cluster_commands["kill_process"].update({f"{item}" : {"?algo" : (self.current_cluster.kill_process, )}})
            #     self.cluster_commands["edit_process_resources"].update({f"{item}" : {"instance count" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}}, 
            #                                                                          "cores" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}},
            #                                                                          "memory" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}},
            #                                                                          "running" : {"<New value" : {"?algo" : (self.current_cluster.edit_process_resources, )}}}})
            #     self.cluster_commands["rename_process"].update({f"{item}" : {"<Process name" : {"?algo" : (self.current_cluster.rename_process, )}}})
                
            # self.cluster_commands["create_computer"]["<computer name"] = {"?algo" : (self.current_cluster.create_computer, )}
            
            for item in clusters.keys():
                
                for jitem in clusters.keys():
                
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}}})
                
        if self.current_root:
            
            if clusters:
            
                for item in clusters.keys():
                    
                    self.root_commands["try_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.try_delete_cluster, )}})
                    self.root_commands["force_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.force_delete_cluster, )}})
                    self.root_commands["rename_cluster"].update({f"{item}" : {"<cluster name" : {"?algo" : (self.current_root.rename_cluster, )}}})
                    
                for item in self.current_root.clusters.keys():
                    
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {}})
                    
                    for jitem in self.current_root.clusters.keys():
                        
                        self.root_commands["relocate_process"]["<process name"][f"{item}"].update({f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}})
                
    
    def exit(self):
        print("Bye Bye")
        sys.stdout.flush()  # Flush output buffer
        sys.exit()  # Terminate the program

    def cicle_through_commands(self, command_dict, shlashed_command, original_command, tab):

        current_step : dict = command_dict

        arguments = []
        
        skips = 1

        try:
            for item in shlashed_command:
                
                if "?non_args" in current_step.keys():
                
                    skips = current_step["?non_args"]
                
                temp = False
                
                temp_item = item
                
                bitem = item

                if item == "?":
   
                    keys = current_step.keys()
                            
                    current_step = ""
                         
                    for coms in keys:
                        
                        if coms != "?non_args" and coms != "?value":
                        
                            if "<" in coms:
                                
                                current_step += coms[1:] + "\n"
                                
                            else:
                                    
                                current_step += coms + "\n"
                                
                    return current_step, "", True, f"{original_command[:-2]}"
                
                if item == "?non_args" or item == "?value":
                    
                    return "Can't type that bruw", "", False, original_command

                if isinstance(current_step, dict) and item not in current_step.keys():
                    
                    for fitem in current_step.keys():
                    
                        if fitem.startswith("<"):
                            
                            temp = True
                            
                            temp_item = fitem
                            
                    if not temp:
                        
                        items = 0
                        
                        finished = ""

                        for keys in current_step.keys():

                            if item in keys:
                                
                                items += 1
                                finished = keys

                        if items == 1 and tab:

                            finished = finished[len(item):]

                            original_command += finished
                            
                            return f"Did you mean {keys}?", "", False, original_command
                        
                        return f"Keyerror: {item}", "", False, original_command
                
                if type(current_step[temp_item]) != tuple:
                    
                    if "?value" in current_step[temp_item].keys():
                        
                        bitem = current_step[temp_item]["?value"]
                
                if bitem != "?algo":
                
                    arguments.append(bitem)
                    
                current_step = current_step[temp_item]
                
            arguments = arguments[skips:]
            
            if not isinstance(current_step, dict):

                return current_step, arguments, True, ""
            
            else:
                
                current_step = "That is not a full command"
                
                return current_step, "", False, original_command
        
        except Exception as e:
            
            print("Something failed", e)

"""
TODO
Explanation : 

"""
        