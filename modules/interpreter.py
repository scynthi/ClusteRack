import os
from os import path as Path
import shlex

from modules.cluster import Cluster
from modules.computer import Computer
from modules.root import Root
import msvcrt
import sys
from colorama import init
init(autoreset=True)

class CLI_Interpreter:
    
    def __init__(self):
        
        # Setup modes
        
        self.current_root : Root = Root(r"./Thing", None)
        self.current_cluster : Cluster = None
        self.current_computer : Computer = None
        self.mode : str = "None"
        
        # Setup runable txt files
        
        self.folder : str = r"./sutoandar"
        self.run : bool = False
        
        # Setup CLI
        
        self.previous_commands : list = []
        self.arguments : list = []
        self.added_commands : list = []
        
        # Commands for different modes
        
        self.root_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "create_cluster" : {"<Cluster name" : {"?algo" : (self.current_root.create_cluster, )}},
            "try_del_cluster" : {},
            "force_del_cluster" : {},
            "relocate_program" : {},
            "move_computer" : {},
            "rename_cluster" : {},
            "cleanup_root" : {"?algo" : (self.current_root.cleanup, )},
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
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {},
            "set_rebalance_algo" : {},
            "run_rebalance" : {},
            "create_computer" : {"<computer name" : {"<cores" : {"<memory" : {}}}},
            "try_del_computer" : {},
            "force_del_computer" : {},
            "rename_computer" : {},
            "edit_computer_resources" : {},
            "get_cluster_programs" : {"?algo" : (self.get_cluster_programs, )},
            "get_cluster_instances" : {"?algo" : (self.get_cluster_instances, )},
            "start_program" : {"<program name" : {"<instance count?" : {"<req cores?" : {"<req memory?" : {}}}}},
            "kill_program" : {},
            "stop_program" : {},
            "edit_program_resources" : {},
            "edit_process_resources" : {},
            "rename_program" : {},
            "add_instance_gen_id" : {"<program name" : {}},
            "add_instance_user_id" : {"<program name" : {"<instance_id" : {}}},
            "edit_instance_status" : {},
            "kill_instance" : {},
            "change_instance_id_gen" : {},
            "change_instance_id_user" : {},
            "cleanup_cluster" : {}
            
        }
        
        self.computer_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {},
            "cleanup_computer" : {}
        }
        
        self.noMode_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}, "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {}
        }
        
        # End setup and go to the input phase
        self.update_dicts()
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
        
        prev_com_index = 0
        
        can_add = True
        
        while True:
            
            #Print out the user input
            sys.stdout.write("\r")
            sys.stdout.write(f"{prompt}>{user_input}")
            sys.stdout.write("\033[K")
            for i in range(len(user_input)-cursor_pos):
                sys.stdout.write("\033[1D")
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
                    sys.stdout.flush()
                
                # After autocomplete put the cursor at the end of the autocompleted
                if type(arguments) == int:
                    cursor_pos += arguments
                    if not can_add:
                        can_add = True
                        self.previous_commands = self.previous_commands[:len(self.added_commands)]
                prev_com_index = 0
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
                    
                    if can_add:
                        
                        self.previous_commands.insert(0, user_input)
                        
                        can_add = False
                    
                    if prev_com_index < len(self.previous_commands) - 1:
                        
                        prev_com_index += 1

                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)

                elif ch2 == b'\x50':  # Down arrow
                    
                    if can_add:
                        
                        self.previous_commands.insert(0, user_input)
                        
                        can_add = False
                    
                    if prev_com_index > 0:
                        
                        prev_com_index -= 1
    
                    if len(self.previous_commands) != 0:
                        
                        user_input = self.previous_commands[prev_com_index]
                        
                    cursor_pos = len(user_input)
                    
                elif ch2 == b'S': # Delete:
                    if cursor_pos < len(user_input):
                        user_input = user_input[:cursor_pos] + user_input[cursor_pos+1:]
                    if not can_add:
                        can_add = True
                        self.previous_commands = self.previous_commands[:len(self.added_commands)]
                    continue
            
            elif key_event == b"?":
                
                user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                cursor_pos += 1
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input}")
                sys.stdout.write("\033[K")
                for i in range(len(user_input)-cursor_pos):
                    sys.stdout.write("\033[1D")
                sys.stdout.flush()
                print() # New line
                if not can_add:
                    can_add = True
                    self.previous_commands = self.previous_commands[:len(self.added_commands)]
                    self.added_commands = []
                self.previous_commands.insert(0, user_input)
                prev_com_index = 0
                break  # Stop input
            
            elif key_event == b"\r": # Enter

                print() # New line
                if not can_add:
                    can_add = True
                    self.previous_commands = self.previous_commands[:len(self.added_commands)]
                    self.added_commands = []
                self.previous_commands.insert(0, user_input)
                prev_com_index = 0
                break  # Stop input
            
            elif key_event == b"\x08": # Backspace
                
                if cursor_pos > 0:
                    user_input = user_input[:cursor_pos-1] + user_input[cursor_pos:]
                    cursor_pos -= 1
                if not can_add:
                    can_add = True
                    self.previous_commands.pop(0)
                continue
            
            elif key_event == b" ": # Space
                
                user_input = user_input[:cursor_pos] + " " + user_input[cursor_pos:]
                cursor_pos += 1
                if not can_add:
                    can_add = True
                    self.previous_commands.pop(0)
                continue
            
            else: # Any other key

                user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                cursor_pos += 1
                if not can_add:
                    can_add = True
                    self.previous_commands.pop(0)
                continue

        self.convert_input(user_input, current_commands)
        
    def cicle_through_commands(self, command_dict, shlashed_command : list, original_command : str, tab, cursor_pos):

        current_step : dict = command_dict

        arguments = []
        
        skips = 1
        cants = ["?non_args", "?value", "?algo"]
        index = 0
        indexes = {}
        
        for item in cants:
            
            if item in original_command:
                
                return f"Can't type that bruw: {item}\n", "", False, original_command
            
        current_index = 0
            
        for item in shlashed_command:
            
            indexes.update({index : item})
            index += len(item) + 1

        try:
            for item in shlashed_command:
                
                is_int = False
                
                if isinstance(current_step, tuple):
                    
                    return "Too many arguments\n", "", False, original_command
                
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
                                
                                if "?" in coms:
                                    
                                    current_step += coms[1:-1] + "\n"
                                    
                                else:
                                
                                    current_step += coms[1:] + "\n"
                                
                            else:
                                    
                                current_step += coms + "\n"
                        
                        items = current_step.split("\n")[:-1]
                                                 
                        for itam in items:
                            
                            if f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}" not in self.added_commands:
                            
                                self.previous_commands.insert(0, f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")
                                self.added_commands.append(f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")

                    return current_step, "", True, f"{original_command[:-2]}"

                if isinstance(current_step, dict) and item not in current_step.keys():
                    
                    for fitem in current_step.keys():
                    
                        if fitem.startswith("<"):
                            
                            if fitem.endswith("?"):
                                
                                temp = True
                                
                                temp_item = fitem
                                
                                is_int = True
                                
                            else:
                            
                                temp = True
                                
                                temp_item = fitem
                            
                    unfinished_item = item
                        
                    for key in indexes.keys():
                            
                        if key < cursor_pos <= key+len(indexes[key]):
                                
                            index = key
                            unfinished_item = indexes[key]
                            break
                        
                    finished = []
                            
                    if not temp:
                    
                        for keys in current_step.keys():
                                
                            if keys[:len(unfinished_item)] == unfinished_item:
                                
                                finished.append(keys)
                                
                        if tab and current_index == index:

                            if len(finished) == 1:
                                
                                finished = finished[0][len(unfinished_item):]
      
                                cursor_pos_diff = index+len(unfinished_item) - cursor_pos
                                
                                if index < cursor_pos <= index+len(unfinished_item):

                                    original_command = original_command[:cursor_pos + cursor_pos_diff] + finished + original_command[cursor_pos + cursor_pos_diff:]
                                
                                return f"Did you mean {keys}?\n", len(finished) + cursor_pos_diff, True, original_command
                            
                            elif len(finished) > 0:
                                
                                keys = finished
                                
                                current_step = ""
                                    
                                for coms in keys:
                                    
                                    if coms != "?non_args" and coms != "?value":
                                    
                                        if "<" in coms:
                                            
                                            if "?" in coms:
                                                
                                                current_step += coms[1:-1] + "\n"
                                                
                                            else:
                                            
                                                current_step += coms[1:] + "\n"
                                            
                                        else:
                                                
                                            current_step += coms + "\n"
                                            
                                    items = current_step.split("\n")[:-1]
                                                 
                                    for itam in items:
                                        
                                        if f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}" not in self.added_commands:
                                        
                                            self.previous_commands.insert(0, f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")
                                            self.added_commands.append(f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")
                                            
                                return current_step, "", False, f"{original_command}"
                            
                            else:
                                
                                return f"No command beggining with {unfinished_item}\n", "", False, f"{original_command}"
                            
                        else:
                            
                            finished = []
                        
                            for keys in current_step.keys():
                                    
                                if keys[:len(item)] == item:
                                    
                                    finished.append(keys)

                            if len(finished) == 1:

                                bitem = finished[0]
                                temp_item = finished[0]
                                
                            elif len(finished) > 0:
                                
                                keys = finished
                                
                                current_step = ""
                                    
                                for coms in keys:
                                    
                                    if coms != "?non_args" and coms != "?value":
                                    
                                        if "<" in coms:
                                            
                                            if "?" in coms:
                                                
                                                current_step += coms[1:-1] + "\n"
                                                
                                            else:
                                            
                                                current_step += coms[1:] + "\n"
                                            
                                        else:
                                                
                                            current_step += coms + "\n"
                                            
                                    items = current_step.split("\n")[:-1]
                                                 
                                    for itam in items:
                                        
                                        if f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}" not in self.added_commands:
                                        
                                            self.previous_commands.insert(0, f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")
                                            self.added_commands.append(f"{original_command[:current_index] + itam + original_command[current_index+len(item):]}")
                                            
                                return current_step, "", False, f"{original_command}"

                            else:
                            
                                if "?" not in item:

                                    return f"No such commands starting with: {item}\n", "", False, original_command
                                
                                if item != "?algo":
                
                                    return f"Keyerror: {item}\n", "", False, original_command
                                
                                else:
                                    return "That is not a full command\n", "", False, original_command 
                        
                current_index += len(item) + 1   

                if type(current_step[temp_item]) != tuple:
                    
                    if "?value" in current_step[temp_item].keys():
                        
                        bitem = current_step[temp_item]["?value"]
                
                if bitem != "?algo":
                    
                    if is_int:
                        
                        bitem = int(bitem)
                
                    arguments.append(bitem)
                    
                current_step = current_step[temp_item]
                
            arguments = arguments[skips:]
            
            if type(current_step) == tuple:

                return current_step, arguments, True, ""
            
            else:
                
                return "That is not a full command\n", "", False, original_command
        
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
            del_args = []
            for i in range(len(default_args)):
                if default_args[i] == "?replace":
                    default_args[i] = arguments[i]
                    del_args.append(arguments[i])
            for i in del_args:
                arguments.remove(i)
            all_args = (*default_args, *arguments)
            returning = func(*all_args)
            
            if returning:
            
                print(returning)
        
        # If we didn't reach the end, or it was just a simple string at the end print it out       
        elif output:

            sys.stdout.write(f"{output}")
            sys.stdout.write("\033[K")
            sys.stdout.flush()
        
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
        
        self.root_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "create_cluster" : {"<Cluster name" : {"?algo" : (self.current_root.create_cluster, )}},
            "try_del_cluster" : {},
            "force_del_cluster" : {},
            "relocate_program" : {},
            "move_computer" : {},
            "rename_cluster" : {},
            "cleanup_root" : {"?algo" : (self.current_root.cleanup, )},
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
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {},
            "set_rebalance_algo" : {},
            "run_rebalance" : {},
            "create_computer" : {"<computer name" : {"<cores?" : {"<memory?" : {}}}},
            "try_del_computer" : {},
            "force_del_computer" : {},
            "rename_computer" : {},
            "edit_computer_resources" : {},
            "get_cluster_programs" : {"?algo" : (self.get_cluster_programs, )},
            "get_cluster_instances" : {"?algo" : (self.get_cluster_instances, )},
            "start_program" : {"<program name" : {"<instance count?" : {"<req cores?" : {"<req memory?" : {}}}}},
            "kill_program" : {},
            "stop_program" : {},
            "edit_program_resources" : {},
            "edit_process_resources" : {},
            "rename_program" : {},
            "add_instance_gen_id" : {"<program name" : {}},
            "add_instance_user_id" : {"<program name" : {"<instance_id" : {}}},
            "edit_instance_status" : {},
            "kill_instance" : {},
            "change_instance_id_gen" : {},
            "change_instance_id_user" : {},
            "cleanup_cluster" : {}
            
        }
        
        self.computer_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {},
            "cleanup_computer" : {}
        }
        
        self.noMode_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}, "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "reload" : {"?algo" : (self.reload, )},
            "update_commands" : {"?algo" : (self.update_dicts, )},
            "run" : {}
        }

        clusters = self.current_root.clusters
        
        if self.current_computer:
            
            self.computer_commands["cleanup_computer"].update({"?algo" : (self.current_computer.cleanup, )})

        if self.current_cluster:
        
            computers = self.current_cluster.computers
            
            self.cluster_commands["set_rebalance_algo"].update({"load_balance" : {"?algo" : (self.current_cluster.set_rebalance_algo, ), "?value" : 0}, "best_fit" : {"?algo" : (self.current_cluster.set_rebalance_algo, ), "?value" : 1}, "fast" : {"?algo" : (self.current_cluster.set_rebalance_algo, ), "?value" : 2}})
                
            for item in computers.keys():
                
                self.cluster_commands["rename_computer"].update({f"{item}" : {"<new name" : {"?algo" : (self.current_cluster.rename_computer, )}}})
                self.cluster_commands["try_del_computer"].update({f"{item}" : {"?algo" : (self.current_cluster.delete_computer, "?replace", "try")}})
                self.cluster_commands["force_del_computer"].update({f"{item}" : {"?algo" : (self.current_cluster.delete_computer, "?replace", "f")}})
                self.cluster_commands["edit_computer_resources"].update({f"{item}" : {"<cores?" : {"<memory?" : {"?algo" : (self.current_cluster.edit_computer_resources, )}}}})
                
            for item in clusters.keys():
                
                self.cluster_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.noMode_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.computer_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                self.root_commands["select"]["cluster"].update({f"{item}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[item]}})
                
            self.cluster_commands["create_computer"]["<computer name"]["<cores?"]["<memory?"].update({"?algo" : (self.current_cluster.create_computer, )})
            self.cluster_commands["run_rebalance"].update({"?algo" : (self.current_cluster.run_rebalance, )})
            self.cluster_commands["start_program"]["<program name"]["<instance count?"]["<req cores?"]["<req memory?"].update({"?algo" : (self.current_cluster.add_program, )})
            
            programs = self.current_cluster.programs.keys()
            
            for program in programs:
            
                self.cluster_commands["kill_program"].update({f"{program}" : {"?algo" : (self.current_cluster.kill_program, )}})
                self.cluster_commands["stop_program"].update({f"{program}" : {"?algo" : (self.current_cluster.stop_program, )}})
                self.cluster_commands["edit_program_resources"].update({f"{program}" : {"instance_count" : {"<New value" : {"?algo" : (self.current_cluster.edit_program_resources, )}},
                                                                                        "cores" : {"<New value" : {"?algo" : (self.current_cluster.edit_program_resources, )}},
                                                                                        "memory" : {"<New value" : {"?algo" : (self.current_cluster.edit_program_resources, )}}}})
                self.cluster_commands["rename_program"].update({f"{program}" : {"<New name" : {"?algo" : (self.current_cluster.rename_program, )}}})
                self.cluster_commands["add_instance_gen_id"].update({f"{program}" : {"?algo" : (self.current_cluster.add_instance, )}})
                self.cluster_commands["add_instance_user_id"].update({f"{program}" : {"<instance_id : " : {"?algo" : (self.current_cluster.add_instance, )}}})
                
            instances = [key for program_name in self.current_cluster.instances.keys() for key in self.current_cluster.instances[program_name].keys()]
            
            for instance in instances:
                
                self.cluster_commands["edit_instance_status"].update({f"{instance}" : {"true" : {"?algo" : (self.cluster_commands, )}, 
                                                                                       "false" : {"?algo" : (self.cluster_commands, )}}})
                self.cluster_commands["kill_instance"].update({f"{instance}" : {"?algo" : (self.current_cluster.kill_instance, )}})
                self.cluster_commands["change_instance_id_gen"].update({f"{instance}" : {"?algo" : (self.current_cluster.change_instance_id, )}})
                self.cluster_commands["change_instance_id_user"].update({f"{instance}" : {"<New instance" : {"?algo" : (self.current_cluster.change_instance_id, )}}})

            self.cluster_commands["cleanup_cluster"].update({"?algo" : (self.current_cluster.cleanup, )})
                
        if clusters:
        
            for cluster in clusters.keys():
                
                self.cluster_commands["select"]["cluster"].update({f"{cluster}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[cluster]}})
                self.noMode_commands["select"]["cluster"].update({f"{cluster}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[cluster]}})
                self.computer_commands["select"]["cluster"].update({f"{cluster}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[cluster]}})
                self.root_commands["select"]["cluster"].update({f"{cluster}" : {"?algo" : (self.select_cluster, ), "?value" : clusters[cluster]}})
                
                self.cluster_commands["select"]["computer"].update({f"{cluster}" : {}})
                self.noMode_commands["select"]["computer"].update({f"{cluster}" : {}})
                self.computer_commands["select"]["computer"].update({f"{cluster}" : {}})
                self.root_commands["select"]["computer"].update({f"{cluster}" : {}})
                
                for program in clusters[cluster].programs.keys():
                
                    self.root_commands["relocate_program"].update({f"{program}" : {}})

                    for origin_cluster in clusters.keys():
                    
                        self.root_commands["relocate_program"][f"{program}"].update({f"{origin_cluster}" : {}})
                        
                        for destination_cluster in clusters.keys():
                            
                            self.root_commands["relocate_program"][f"{program}"][f"{origin_cluster}"].update({f"{destination_cluster}" : {"?algo" : (self.current_root.relocate_program, )}})
                    
                for computers in clusters[cluster].computers.keys():
                    
                    if computers:
                    
                        self.cluster_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.noMode_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.computer_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.root_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        
                        self.root_commands["move_computer"].update({f"{computers}" : {}})
                        
                        for origin_cluster in clusters.keys():
                            
                            self.root_commands["move_computer"][f"{computers}"].update({origin_cluster : {}})
                            
                            for destination_cluster in clusters.keys():
                                
                                self.root_commands["move_computer"][f"{computers}"][f"{origin_cluster}"].update({destination_cluster : {"?algo" : (self.current_root.move_computer, )}})
                                
                self.root_commands["try_del_cluster"].update({f"{cluster}" : {"?algo" : (self.current_root.delete_cluster, "?replace", "try")}})
                self.root_commands["force_del_cluster"].update({f"{cluster}" : {"?algo" : (self.current_root.delete_cluster, "?replace", "f")}})
                self.root_commands["rename_cluster"].update({f"{cluster}" : {"<New name" : {"?algo" : (self.current_root.rename_cluster, )}}})

                
            
            # for item in self.current_cluster.processes.keys():
                
            #     self.cluster_commands["kill_process"].update({f"{item}" : {"?algo" : (self.current_cluster.kill_process, )}})
            #     self.cluster_commands["edit_process_resources"].update({f"{item}" : {"instance count" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}}, 
            #                                                                          "cores" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}},
            #                                                                          "memory" : {"<New value (int)" : {"?algo" : (self.current_cluster.edit_process_resources, )}},
            #                                                                          "running" : {"<New value" : {"?algo" : (self.current_cluster.edit_process_resources, )}}}})
            #     self.cluster_commands["rename_process"].update({f"{item}" : {"<Process name" : {"?algo" : (self.current_cluster.rename_process, )}}})
                    
                    
        
        if self.folder:
            
            files = os.listdir(self.folder)
            
            for text_file in files:
                
                self.noMode_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.computer_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.root_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                self.cluster_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                
    def get_cluster_programs(self):
        
        programs = [item for item in self.current_cluster.instances.keys()]
        
        if len(programs) > 0:
            for program in programs:
                print(program)
        else:
            print("No programs")
        
            
    def get_cluster_instances(self):
        
        programs = [item for item in self.current_cluster.instances.keys()]
        
        instances = []
        
        for program in programs:
            
            instances.append([program, *self.current_cluster.instances[program].keys()])
        
        if len(instances) > 0:
            for instance in instances:
                for item in instance:
                    print(item, end=" ")
                print()
        else:
            print("No instances")
            
    
    def reload(self):
        
        os.execv(sys.executable, ['python'] + sys.argv)

    def exit(self):

        sys.stdout.flush()  # Flush output buffer
        sys.exit()  # Terminate the program