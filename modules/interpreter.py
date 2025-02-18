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
        
        # Setup modes
        
        self.current_root : Root = Root(r"./Thing", "ui")
        self.current_cluster : Cluster = None
        self.current_computer : Computer = None
        self.mode : str = "None"
        
        # Setup runable txt files
        
        self.folder : str = r"./sutoandar"
        self.run : bool = False
        
        # Setup CLI
        
        self.previous_commands : list = []
        self.arguments : list = []
        
        # Commands for different modes
        
        self.root_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "create_cluster" : {"<cluster name" : {"?algo" : (self.current_root.create_cluster, )}},
            "try_del_cluster" : {},
            "force_del_cluster" : {},
            "relocate_process" : {"<process name" : {}},
            "move_computer" : (self.current_root.move_computer, ),
            "rename_cluster" : {},
            "run" : {}
        }

        self.cluster_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            # "set_default_rebalance_algo" : {"load_balance" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}, "best_fit" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}, "fast" : {"?algo" : (self.current_cluster.set_default_rebalance_algo, )}},
            # "run_default_rebalance" : {"?algo" : (self.current_cluster.run_default_rebalance_algo, )},
            # "run_rebalance" : {"?algo" : (self.current_cluster.run_default_rebalance_algo, )},
            "create_computer" : {"<computer name" : {}},
            "try_del_computer" : {},
            "force_del_computer" : {},
            "rename_computer" : {},
            # "start_process" : {"<process name" : {"<running" : {"<cpu_req" : {"<ram_req" : {"<instance_count" : {"<date_started" : {"?algo" : (self.current_cluster.start_process, )}}}}}}},
            "kill_process" : {},
            "edit_process_resources" : {},
            "rename_process" : {},
            "run" : {}
        }
        
        self.computer_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "run" : {},
            "edit_resources" : {},
            "get_program_instances" : {}
        }
        
        self.noMode_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}, "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "run" : {}
        }
        
        # Add all possible cluster/computer names for autocomplete
        
        clusters = self.current_root.clusters
        
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
                    
                    if comps:
                    
                        self.cluster_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                        self.noMode_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                        self.computer_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
                        self.root_commands["select"]["computer"][f"{item}"].update({f"{comps}" : {"?value" : clusters[item].computers[comps], "?algo" : (self.select_computer, )}, "?value" : clusters[item]})
        
        # End setup and go to the input phase
        self.update_dicts
        self.take_input("")

# Input handling and converting             
                
    def take_input(self, default_text):
        
        # Make a dict to store the current modes avaliable commands
        
        current_commands : dict
        
        # match the current mode to show the correct mode in CMD and select the correct commands
        
        match self.mode.lower():
            
            case "computer":
                
                prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>{self.current_computer.name.capitalize()}"
                current_commands = self.computer_commands
                
            case "cluster":
                
                prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}"
                current_commands = self.cluster_commands
                
            case "root":
                
                prompt = f"{self.current_root.name.capitalize()}"
                current_commands = self.root_commands
                
            case _:
                
                prompt = "None"
                current_commands = self.noMode_commands
                
        # If there is something in the default text print it into the input

        user_input = f"{default_text}"
        if len(user_input) > 0: cursor_pos = len(user_input) 
        else: cursor_pos = 0
        
        # Print out the prompt
        
        sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
        sys.stdout.flush()
        
        # Setup up/down arrow usage
        
        prev_com_index = -1
        
        while True:
            
            #Print out the user input
            sys.stdout.write("\r")
            sys.stdout.write(f"{prompt}>{user_input[:cursor_pos]}|{user_input[cursor_pos:]}")
            sys.stdout.write("\033[K")
            sys.stdout.flush()
            
            # Get the input
            
            key_event = msvcrt.getch()
                
            if key_event == b"\t": # Tab
                
                current_step, arguments, success, user_input = self.cicle_through_commands(current_commands, shlex.split(user_input), user_input, True, cursor_pos)
                if not success:
                    
                    # Special case
                    # If the autocomplete was unsuccsessful print out the current_step
                    sys.stdout.write("\n")
                    sys.stdout.write(f"{current_step}")
                    sys.stdout.write("\033[K")
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                
                # After autocomplete put the cursor at the end of the autocompleted
                if type(arguments) == int:
                    cursor_pos += arguments
                continue
            
            elif key_event == b'\x00' or key_event == b'\xe0': # Special key, like the arrow keys
                
                # Get the second part of the bytes
                ch2 = msvcrt.getch()
                
                if ch2 == b'\x4b':  # Left arrow
                    if cursor_pos > 0:
                        cursor_pos -= 1
                        sys.stdout.write("\033[1D")
                        
                elif ch2 == b'\x4d':  # Right arrow
                    if cursor_pos < len(user_input):
                        cursor_pos += 1
                        sys.stdout.write("\033[1C")
                        
                elif ch2 == b'\x48':  # Up arrow
                    
                    if prev_com_index < len(self.previous_commands) - 1:
                        
                        prev_com_index += 1

                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)

                elif ch2 == b'\x50':  # Down arrow
                    
                    if prev_com_index > 0:
                        
                        prev_com_index -= 1
    
                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)
                    
                elif ch2 == b'S': # Delete:
                    if cursor_pos < len(user_input):
                        user_input = user_input[:cursor_pos] + user_input[cursor_pos+1:]
                    continue
                    
            
            elif key_event == b"\r": # Enter

                print() # New line
                if "\x00" in user_input:
                    
                    user_input = user_input.replace("\x00", "")
                self.previous_commands.insert(0, user_input)
                break  # Stop input
            
            elif key_event == b"\x08": # Backspace
                
                if cursor_pos > 0:
                    user_input = user_input[:cursor_pos-1] + user_input[cursor_pos:]
                    cursor_pos -= 1
                continue
            
            elif key_event == b" ": # Space
                
                user_input = user_input[:cursor_pos] + " " + user_input[cursor_pos:]
                cursor_pos += 1
                continue
            
            else: # Any other key

                user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                cursor_pos += 1
                continue

        self.convert_input(user_input, current_commands)
        
    def cicle_through_commands(self, command_dict, shlashed_command : list, original_command : str, tab, cursor_pos):

        current_step : dict = command_dict

        arguments = []
        
        skips = 1
        cants = ["?non_args", "?value", "?algo"]
        
        for item in cants:
            
            if item in original_command:
                
                return f"Can't type that bruw: {item}", "", False, original_command

        try:
            for item in shlashed_command:
                
                if isinstance(current_step, tuple):
                    
                    return "Too many arguments", "", False, original_command
                
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

                if isinstance(current_step, dict) and item not in current_step.keys():
                    
                    for fitem in current_step.keys():
                    
                        if fitem.startswith("<"):
                            
                            temp = True
                            
                            temp_item = fitem
                            
                    if not temp:
                        
                        finished = []

                        for keys in current_step.keys():
                                
                            if keys[:len(item)] == item:
                                
                                finished.append(keys)
                                
                        if tab:

                            if len(finished) == 1:
                                
                                finished = finished[0]

                                finished = finished[len(item):]
                                
                                cursor_pos_diff = original_command.index(item)+len(item) - cursor_pos
                                
                                if original_command.index(item) < cursor_pos <= original_command.index(item)+len(item):

                                    original_command = original_command[:cursor_pos + cursor_pos_diff] + finished + original_command[cursor_pos + cursor_pos_diff:]
                                
                                return f"Did you mean {keys}?", len(finished) + cursor_pos_diff, True, original_command
                            
                            elif len(finished) > 0:
                                
                                keys = finished
                                
                                current_step = ""
                                    
                                for coms in keys:
                                    
                                    if coms != "?non_args" and coms != "?value":
                                    
                                        if "<" in coms:
                                            
                                            current_step += coms[1:] + "\n"
                                            
                                        else:
                                                
                                            current_step += coms + "\n"
                                            
                                return current_step, "", False, f"{original_command}"
                            
                            else:
                                
                                return f"No command beggining with {item}", "", False, f"{original_command}"
                        
                        if "?" not in item:
    
                            return f"Keyerror: {item}", "", False, original_command
                        
                        return "That is not a full command", "", False, original_command
                
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
            
    def convert_input(self, command, current_commands):
        
        # Cut up the command (this library allow the usage of spaces by putting it between quotation marks)
        # Put ?algo at the end to get the algorythm at the end
        shlashed_command = shlex.split(command)
        shlashed_command.append("?algo")
        
        try:

            output, arguments, success, default_text = self.cicle_through_commands(current_commands, shlashed_command, command, False, 0)

        except Exception as e:

            print(f"Something went wrong {e}")
            return self.take_input("")
        
        # If the output is a tuple (meaning we reached the end of the dict), unpack the tuple and run the function         
        if isinstance(output, tuple):
            
            func, *default_args = output
            all_args = (*default_args, *arguments)
            returning = func(*all_args)
            
            if returning:
            
                print(returning)
        
        # If we didn't reach the end, or it was just a simple string at the end print it out       
        elif output:
                    
            print(output)
        
        self.update_dicts()
        
        # If we gave a runnable text file don't ask for input
        if not self.run:
            
            self.take_input(f"{default_text}")
    
# File reading
    
    def select_run_folder(self, folder_name):
        
        self.folder = fr"./{folder_name}"
        
        self.update_dicts()
        
    
    def read_file(self, file_name):
        
        file = Path.join(self.folder, file_name)
        
        with open(file, "r") as f:
            
            temp_commands = f.readlines()
            f.close()
        
        commands = []
            
        for coms in temp_commands:
            
            commands.append(coms.replace("\n", ""))
            
        print(commands)
        
        self.run = True
        current_commands : dict = {}
            
        for item in commands:
            
            match self.mode.lower():
            
                case "computer":
                    
                    prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>{self.current_computer.name.capitalize()}>"
                    current_commands = self.computer_commands
                case "cluster":
                    
                    prompt = f"{self.current_root.name.capitalize()}>{self.current_cluster.name.capitalize()}>"
                    current_commands = self.cluster_commands
                case "root":
                    
                    prompt = f"{self.current_root.name.capitalize()}>"
                    current_commands = self.root_commands
                case _:
                    
                    prompt = "None>"
                    current_commands = self.noMode_commands

            print(f"{prompt}{item}")
            self.convert_input(item, current_commands)
            
        self.run = False
    
# Mode selection

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
        
# Miscellaneous

    def update_dicts(self):

        clusters = self.current_root.clusters
        
        if self.current_computer:
            
            self.computer_commands["get_program_instances"].update({"?algo" : (self.current_computer.get_prog_instances, )})
            
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
                
            self.cluster_commands["create_computer"]["<computer name"].update({"<cores" : {"<memory" : {"?algo" : (self.current_cluster.create_computer, )}}})
            
            for item in clusters.keys():
                
                for jitem in clusters.keys():
                
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}}})
        
        if self.current_root:
            
            if clusters:
            
                for item in clusters.keys():
                    
                    # self.root_commands["try_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.try_delete_cluster, )}})
                    # self.root_commands["force_del_cluster"].update({f"{item}" : {"?algo" : (self.current_root.force_delete_cluster, )}})
                    self.root_commands["rename_cluster"].update({f"{item}" : {"<cluster name" : {"?algo" : (self.current_root.rename_cluster, )}}})
                    
                for item in self.current_root.clusters.keys():
                    
                    self.root_commands["relocate_process"]["<process name"].update({f"{item}" : {}})
                    
                    for jitem in self.current_root.clusters.keys():
                        
                        self.root_commands["relocate_process"]["<process name"][f"{item}"].update({f"{jitem}" : {"?algo" : (self.current_root.relocate_process, )}})
        
        if self.folder:
            
            files = os.listdir(self.folder)
            
            print(files)
            
            for text_file in files:
                
                self.noMode_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.computer_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.root_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.cluster_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                
    def exit(self):

        sys.stdout.flush()  # Flush output buffer
        sys.exit()  # Terminate the program