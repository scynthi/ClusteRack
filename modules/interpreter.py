import os
from os import path as Path
import shlex
from colorama import Fore, Style, Back
from modules.cluster import Cluster
from modules.computer import Computer
from modules.root import Root
import msvcrt
import sys
import ctypes
from ctypes import c_long, c_wchar_p, c_ulong, c_void_p, Structure, byref, wintypes
from colorama import init

init(autoreset=True)

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_uint16), ("srWindow", ctypes.c_uint16),
                ("dwMaximumWindowSize", COORD)]

class CLI_Interpreter:
    
    def __init__(self, root = ""):
        
        # Ask the root path
        while not Path.exists(root):
        
            root = self.add_root()
            
            if not Path.exists(root):
                
                print("Invalid path")
                
        # Setup modes
        self.current_root : Root = Root(root, None)
        self.current_cluster : Cluster = None
        self.current_computer : Computer = None
        self.mode : str = "None"
        
        # Basic things
        
        STD_OUTPUT_HANDLE = -11
        self.console_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        self.kernel32 = ctypes.windll.kernel32
        self.hStdOut = self.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        
        self.set_fixed_console_size(160, 25)
        
        # For the descriptions
        self.desc_folder = r"./Assets/Descriptions"
        
        # Setup runable txt files
        self.folder : str = ""
        self.run : bool = False
        
        # Setup CLI
        self.previous_commands : list = []
        self.arguments : list = []
        self.added_commands : list = []
        
        # End setup and go to the input phase
        self.update_dicts()
        self.take_input("")
        
    def set_fixed_console_size(self, width, height):
        # Set buffer size
        buffer_size = wintypes._COORD(width, height)
        ctypes.windll.kernel32.SetConsoleScreenBufferSize(self.hStdOut, buffer_size)
        
        # Set window size
        rect = wintypes.SMALL_RECT(0, 0, width - 1, height - 1)
        ctypes.windll.kernel32.SetConsoleWindowInfo(self.hStdOut, ctypes.c_bool(True), ctypes.byref(rect))

# Input handling and converting      

    def get_cursor_position(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if self.kernel32.GetConsoleScreenBufferInfo(self.hStdOut, ctypes.byref(csbi)):
            return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y
        else:
            return None     
                
    def take_input(self, default_text):
        
        # Make a dict to store the current modes avaliable commands
        current_commands : dict
        add_start_cursor = 0
        
        # match the current mode to show the correct mode in CMD and select the correct commands 
        match self.mode.lower():
            
            case "computer":
                
                prompt = f"{Fore.BLACK}{Back.CYAN}{self.current_root.name}{Back.RESET+Fore.RESET}>{Fore.BLACK}{Back.WHITE}{self.current_cluster.name}{Back.RESET+Fore.RESET}>{Fore.WHITE + Style.BRIGHT}{self.current_computer.name}{Back.RESET+Fore.RESET+Style.RESET_ALL}"
                add_start_cursor = len(f"{self.current_root.name}{self.current_cluster.name}{self.current_computer.name}")+3
                current_commands = self.computer_commands
                
            case "cluster":
                
                prompt = f"{Fore.BLACK}{Back.CYAN}{self.current_root.name}{Back.RESET+Fore.RESET}>{Fore.BLACK}{Back.WHITE}{self.current_cluster.name}{Back.RESET+Fore.RESET}"
                add_start_cursor = len(f"{self.current_root.name}{self.current_cluster.name}")+2
                current_commands = self.cluster_commands
                
            case "root":
                
                prompt = f"{Fore.BLACK}{Back.CYAN}{self.current_root.name}{Back.RESET+Fore.RESET}"
                add_start_cursor = len(f"{self.current_root.name}")+1
                current_commands = self.root_commands
                
            case _:
                prompt = f"{Fore.BLACK}{Back.LIGHTCYAN_EX}User{Back.RESET+Fore.RESET}"
                current_commands = self.noMode_commands
                add_start_cursor = 5
                
        # If there is something in the default text insert it into the input
        user_input = f"{default_text}"
        if len(user_input) > 0: cursor_pos = len(user_input) 
        else: cursor_pos = 0
        
        # Setup up/down arrow usage
        prev_com_index = 0
        can_add = True
        cursor_x, cursor_y = self.get_cursor_position()
        
        while True:
            
            cols = os.get_terminal_size().columns
            position = (cursor_y << 16) | cursor_x  # Combine x and y into a single value
            ctypes.windll.kernel32.SetConsoleCursorPosition(self.console_handle, position)
            sys.stdout.write("\033[K")
            sys.stdout.write("\033[J")
            sys.stdout.write(f"{prompt}>{user_input}")
            sys.stdout.write("\033[K")
            add_pos_x = cursor_x + cursor_pos + add_start_cursor
            lines = add_pos_x // cols
            add_pos_y = cursor_y
            if lines > 0:
                add_pos_x -= lines*cols
                add_pos_y += lines
            position = (add_pos_y << 16) | add_pos_x
            ctypes.windll.kernel32.SetConsoleCursorPosition(self.console_handle, position)
            # for i in range(len(user_input)-cursor_pos):
            #     sys.stdout.write("\033[1D")
            sys.stdout.flush()
            
            # Get the input
            key_event = msvcrt.getch()
                
            if key_event == b"\t": # Tab
                
                can_add = self._delete_choosable_commands(can_add)
                # Finish the input
                self.previous_commands.insert(0, user_input)
                prev_com_index = 0
                
                try:
                    current_step, arguments, success, user_input = self.cicle_through_commands(current_commands, shlex.split(user_input), user_input, True, cursor_pos)
                    if not success:
                        
                        # Special case
                        # If the autocomplete was unsuccsessful print out the current_step
                        sys.stdout.write("\n")
                        sys.stdout.write(f"{current_step}")
                        sys.stdout.write("\033[K")
                        sys.stdout.flush()
                        cursor_x, cursor_y = self.get_cursor_position()
                    
                    # After autocomplete put the cursor at the end of the autocompleted
                    if type(arguments) == int:
                        
                        cursor_pos += arguments
                        
                        # If there are suggestions delete them out of the choosable commands
                        can_add = self._delete_choosable_commands(can_add)
                    prev_com_index = 0
                except:
                    print("A mappa név előtt nem lehet idézőjel beküldés előtt")
                continue
            
            elif key_event == b'\x00' or key_event == b'\xe0': # Special key, like the arrow keys
                
                # Get the second part of the byte
                ch2 = msvcrt.getch()
                
                if ch2 == b'\x4b':  # Left arrow
                    if cursor_pos > 0:
                        cursor_pos -= 1
                        
                elif ch2 == b'\x4d':  # Right arrow
                    if cursor_pos < len(user_input):
                        cursor_pos += 1
                        
                        
                elif ch2 == b'\x48':  # Up arrow
                    
                    # Enable the usage of suggestions
                    if can_add:  
                        self.previous_commands.insert(0, user_input)
                        can_add = False
                    
                    # Choose an older command/suggestion
                    if prev_com_index < len(self.previous_commands) - 1:
                        prev_com_index += 1

                    if len(self.previous_commands) != 0:
                        user_input = self.previous_commands[prev_com_index]
                    
                    # Put the cursor at the correct position
                    cursor_pos = len(user_input)

                elif ch2 == b'\x50':  # Down arrow
                    
                    # Enable the usage of suggestions
                    if can_add:
                        self.previous_commands.insert(0, user_input)
                        can_add = False
                    
                    # Choose an older command/suggestion
                    if prev_com_index > 0:
                        prev_com_index -= 1
    
                    if len(self.previous_commands) != 0:
                        user_input = self.previous_commands[prev_com_index]
                    
                    # Put the cursor at the correct position
                    cursor_pos = len(user_input)
                    
                elif ch2 == b'S': # Delete:
                    
                    # Delete the character after the cursor
                    if cursor_pos < len(user_input):
                        user_input = user_input[:cursor_pos] + user_input[cursor_pos+1:]

                    continue

                elif ch2 == b'G': # Home

                    cursor_pos = 0

                elif ch2 == b'O': # End

                    cursor_pos = len(user_input)
            
            elif key_event == b"?": #question mark
                
                # Add the question mark and print out the command
                user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                cursor_pos += 1
                sys.stdout.write("\r")
                sys.stdout.write(f"{prompt}>{user_input}")
                sys.stdout.write("\033[K")
                for i in range(len(user_input)-cursor_pos):
                    sys.stdout.write("\033[1D")
                sys.stdout.flush()
                print()
                cursor_x, cursor_y = self.get_cursor_position()
                
                # Finish the input
                self.previous_commands.insert(0, user_input)
                prev_com_index = 0
                break
            
            elif key_event == b"\r": # Enter

                print() # Print the new line
                
                can_add = self._delete_choosable_commands(can_add)
                # Finish the input
                self.previous_commands.insert(0, user_input)
                prev_com_index = 0
                break
            
            elif key_event == b"\x08": # Backspace
                
                # Delete the character before the cursor
                if cursor_pos > 0:
                    user_input = user_input[:cursor_pos-1] + user_input[cursor_pos:]
                    cursor_pos -= 1
                    
                continue
            
            elif key_event == b" ": # Space
                
                # Put a space in the command
                user_input = user_input[:cursor_pos] + " " + user_input[cursor_pos:]
                cursor_pos += 1
                
                continue
            
            else: # Any other key

                # Put the character into the command
                try:
                    user_input = user_input[:cursor_pos] + key_event.decode('utf-8') + user_input[cursor_pos:]
                    cursor_pos += 1
                    
                    continue
                except:
                    print("\nThat character can't be decoded")
                    cursor_x, cursor_y = self.get_cursor_position()
                    continue
        
        # Finish the input 
        self.convert_input(user_input, current_commands)
        
    def _delete_choosable_commands(self, can_add):
        """If there are suggestions delete them out of the choosable commands"""
        
        if not can_add and len(self.added_commands) > 0:
            self.previous_commands = self.previous_commands[len(self.added_commands)+1:]
            self.added_commands = []
            return True
        amount = self.previous_commands.count("")
        for i in range(amount):
            self.previous_commands.remove("")
        return False
        
    def convert_input(self, command, current_commands):
        
        # Cut up the command (this library allow the usage of spaces by putting it between quotation marks)
        # Put ?algo at the end to get the algorythm at the end
        try:
            shlashed_command = shlex.split(command)
        except:
            print("A mappa név előtt nem lehet idézőjel beküldés előtt")
            return self.take_input(command)
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
            func(*all_args)
        
        # If output is a string, print it out      
        elif output:
            sys.stdout.write(f"{output}")
            sys.stdout.write("\033[K")
            sys.stdout.flush()
        
        self.update_dicts()
        
        # If we gave a runnable text file don't ask for input
        if not self.run:
            self.take_input(f"{default_text}")
            
    def cicle_through_commands(self, command_dict, shlashed_command : list, original_command : str, tab, cursor_pos):

        # Setup the returns
        current_step = command_dict
        arguments = []
        
        # Setup the helper variables
        skips = 1
        restricted_words = ["?non_args", "?value", "?algo", "?desc"]
        index = 0
        indexes = {}
        current_index = 0
        
        # If "/?" is in the command, print out the command description
        if "/?" in original_command:
            original_command = f"{shlashed_command[0]} /?"
            shlashed_command = [shlashed_command[0], "?desc", "?algo"]
        
        # If the command includes a restriced word, return an error message
        for item in restricted_words:
            if item in original_command:
                return f"\n{Fore.BLACK}{Back.RED}The command includes a restriced word: {item}\n\n{Fore.RESET+Back.RESET}", "", False, original_command
        
        # Give each word an index in the command, used for autocorrect
        for item in shlashed_command:
            if " " not in item:
                indexes.update({index : item})
                index += len(item) + 1
            else:
                index += 1
                indexes.update({index : item})
                index += len(item) + 2

        # Cicle the shlashed_command through the dictionary
        try:

            for current_word in shlashed_command:
                
                
                is_current_item_int = False
                can_autocomplete = True
                changable_item = current_word
                argument_item = current_word
                
                if isinstance(current_step, tuple):
                    return "Too many arguments\n", "", False, original_command
                
                if "?non_args" in current_step.keys():
                    skips = current_step["?non_args"]

                # Print out what the input can be
                if current_word == "?":
                    current_step = self._return_avaliable_commands(current_step, original_command, current_index, current_word, current_step.keys(), restricted_words)
                    return current_step, "", True, f"{original_command[:-2]}"
                
                # If the current current_word isn't in the current_step, check if it can be extended, or is just an current_word that is supposed to be whatever the user wants
                if isinstance(current_step, dict) and current_word not in current_step.keys():
                    
                    # If a key starts with "<" go that direction, the autocomplete should come first just in case, but in this context this is perfictly OK
                    for key in current_step.keys():
                        if key.startswith("<"):
                
                            if key.endswith("?"):
                                can_autocomplete = False
                                changable_item = key
                                is_current_item_int = True
                                
                            else:
                                can_autocomplete = False       
                                changable_item = key
                    
                    # Save the current_word in a temporary variable       
                    unfinished_item = current_word
                    finished = []
                    
                    # Check what word we are autocompleting
                    for key in indexes.keys():
                        if key < cursor_pos <= key+len(indexes[key]): 
                            index = key
                            unfinished_item = indexes[key]
                            break

                    if can_autocomplete:
                        
                        # Check what words begin with the unfinished_word
                        for keys in current_step.keys():
                            if keys[:len(unfinished_item)] == unfinished_item:
                                finished.append(keys)
                        
                        # If we pressed Tab, and the cursor is in an ok position    
                        if tab and current_index == index:
                            
                            # If there is only one word
                            if len(finished) == 1:
                                finished = finished[0]
                                if " " not in finished:
                                    finished = finished[len(unfinished_item):]
                                    cursor_pos_diff = index+len(unfinished_item) - cursor_pos
                                    
                                    if index < cursor_pos <= index+len(unfinished_item):
                                        original_command = original_command[:cursor_pos + cursor_pos_diff] + finished + original_command[cursor_pos + cursor_pos_diff:]
                                    
                                    return "", len(finished) + cursor_pos_diff, True, original_command
                                else:
                                    finished = f'"{finished}"'
                                    cursor_pos_diff = index+len(unfinished_item) - cursor_pos
                                    
                                    if index < cursor_pos <= index+len(unfinished_item):
                                        original_command = original_command[:cursor_pos + cursor_pos_diff-len(unfinished_item)] + finished + original_command[cursor_pos + cursor_pos_diff:]
                                    
                                    return "", len(finished) - 1 + cursor_pos_diff, True, original_command
                            
                            # If there are more than one words
                            elif len(finished) > 0:
                                current_step = self._return_avaliable_commands(current_step, original_command, current_index, current_word, finished, restricted_words)         
                                return current_step, "", False, f"{original_command}"
                            
                            else:
                                return f"No command beggining with {unfinished_item}\n", "", False, f"{original_command}"
                            
                        else:
                            
                            # Check what words begin with the current_word
                            finished = []
                            for keys in current_step.keys():   
                                if keys[:len(current_word)] == current_word:
                                    finished.append(keys)
                                    
                            # If there is only one word
                            if len(finished) == 1:
                                argument_item = finished[0]
                                changable_item = finished[0]
                            
                            # More than one words
                            elif len(finished) > 0:
                                current_step = self._return_avaliable_commands(current_step, original_command, current_index, current_word, finished, restricted_words)           
                                return current_step, "", False, f"{original_command}"
                            
                            # No words begining with the current_word
                            else:
                                # Return the Keyerror, else the command in not finished
                                if "?" not in current_word:
                                    return f"Keyerror: {current_word}\n", "", False, original_command
                                else:
                                    return "That is not a full command\n", "", False, original_command
                
                # Add to the current index (+1 for the spaces) 
                if " " not in current_word:
                    current_index += len(current_word) + 1
                else:
                    current_index += len(current_word) + 3

                # If the next step isn't the end point, if it has "?value" in it's keys, add the value as an argument
                if type(current_step[changable_item]) != tuple:
                    if "?value" in current_step[changable_item].keys():
                        argument_item = current_step[changable_item]["?value"]

                if is_current_item_int:
                    
                    try:
                        
                        argument_item = int(argument_item)
                        
                    except:
                        
                        return "Command wrongly entered\n", "", False, original_command
                
                # Go further in the dictionary
                arguments.append(argument_item)
                current_step = current_step[changable_item]

            # Exclude the skips, -1 for the ?algo we added at the end
            arguments = arguments[skips:-1]
            
            # If we reached the end return
            if type(current_step) == tuple:
                return current_step, arguments, True, ""
            else:
                return "That is not a full command\n", "", False, original_command
        
        except Exception as e:
            
            print("Something failed", e)
            
    def _return_avaliable_commands(self, current_step, original_command, current_index, current_word, keys, restricted_words):
                            
        current_step = ""
                
        for command in keys:
            if command not in restricted_words:

                # Put the command into the current_step
                if "<" in command: 
                    if "?" in command:  
                        current_step += command[1:-1] + "\n"  
                    else:
                        current_step += command[1:] + "\n"  
                else:
                    if " " in command:
                        current_step += f'"{command}"' + "\n"
                    else: 
                        current_step += command + "\n"

            # Put suggestions into previous_commands
            command_items = current_step.split("\n")[:-1]                    
            for item in command_items:
                if f"{original_command[:current_index] + item + original_command[current_index+len(current_word):]}" and item not in self.added_commands:
                    self.previous_commands.insert(0, f"{original_command[:current_index] + item + original_command[current_index+len(current_word):]}")
                    self.added_commands.append(item)
                    
        return current_step
            
# File reading
    
    def select_run_folder(self, folder_name):
        
        if Path.exists(fr"./{folder_name}"):
            self.folder = fr"./{folder_name}"
            self.update_dicts()
        else:
            print("Folder doesn't exist")
        
    
    def read_file(self, file_name):
        
        if Path.exists(self.folder):
        
            # Get the content of the file
            file = Path.join(self.folder, file_name)
            with open(file, "r") as f:
                content = f.readlines()
                f.close()
            
            # Split the content, and put it into commands
            commands = [] 
            for coms in content:  
                commands.append(coms.replace("\n", ""))
                
            print(commands)
            
            # Setup running the file
            self.run = True
            current_commands : dict = {}
            
            # Run the file 
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
        else:
            
            print("Doesn't have a valid run folder")
    
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
        
# Miscellaneous ===============================================================================

    def update_dicts(self):
        """Can't really comment anything here, just updating the dictionaries"""
        
        self.root_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}},
                "?desc" : {"?algo" : (self.run_desc, "select.txt"), "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "save_amount" : {"<Name" : {"<How far back?": {"?algo" : (self.save_prev, )}}, "?desc" : {"?algo" : (self.run_desc, "save_amount.txt"), "?non_args" : 2}},
            "save_all" : {"<Name" : {"?algo" : (self.save_prev, "?replace", "all")}, "?desc" : {"?algo" : (self.run_desc, "save_all.txt"), "?non_args" : 2}},
            "reload" : {"?algo" : (self.reload, ), "?desc" : {"?algo" : (self.run_desc, "reload.txt"), "?non_args" : 2}},
            "update_commands" : {"?algo" : (self.update_dicts, ), "?desc" : {"?algo" : (self.run_desc, "update_commands.txt"), "?non_args" : 2}},
            "create_cluster" : {"<Cluster name" : {"?algo" : (self.current_root.create_cluster, )}, "?desc" : {"?algo" : (self.run_desc, "create_cluster.txt"), "?non_args" : 2}},
            "try_del_cluster" : {"?desc" : {"?algo" : (self.run_desc, "try_del_cluster.txt"), "?non_args" : 2}},
            "force_del_cluster" : {"?desc" : {"?algo" : (self.run_desc, "force_del_cluster.txt"), "?non_args" : 2}},
            "relocate_program" : {"?desc" : {"?algo" : (self.run_desc, "relocate_program.txt"), "?non_args" : 2}},
            "move_computer" : {"?desc" : {"?algo" : (self.run_desc, "move_computer.txt"), "?non_args" : 2}},
            "rename_cluster" : {"?desc" : {"?algo" : (self.run_desc, "rename_cluster.txt"), "?non_args" : 2}},
            "cleanup_root" : {"?algo" : (self.current_root.cleanup, ), "?desc" : {"?algo" : (self.run_desc, "cleanup_root.txt"), "?non_args" : 2}},
            "run" : {"?desc" : {"?algo" : (self.run_desc, "run.txt"), "?non_args" : 2}}
        }

        self.cluster_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}},
                "?desc" : {"?algo" : (self.run_desc, "select.txt"), "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "save_amount" : {"<Name" : {"<How far back?": {"?algo" : (self.save_prev, )}}, "?desc" : {"?algo" : (self.run_desc, "save_amount.txt"), "?non_args" : 2}},
            "save_all" : {"<Name" : {"?algo" : (self.save_prev, "?replace", "all")}, "?desc" : {"?algo" : (self.run_desc, "save_all.txt"), "?non_args" : 2}},
            "reload" : {"?algo" : (self.reload, ), "?desc" : {"?algo" : (self.run_desc, "reload.txt"), "?non_args" : 2}},
            "update_commands" : {"?algo" : (self.update_dicts, ), "?desc" : {"?algo" : (self.run_desc, "update_commands.txt"), "?non_args" : 2}},
            "run" : {"?desc" : {"?algo" : (self.run_desc, "run.txt"), "?non_args" : 2}},
            "set_rebalance_algo" : {"?desc" : {"?algo" : (self.run_desc, "set_rebalance_algo.txt"), "?non_args" : 2}},
            "run_rebalance" : {"?desc" : {"?algo" : (self.run_desc, "run_rebalance.txt"), "?non_args" : 2}},
            "create_computer" : {"<computer name" : {"<cores?" : {"<memory?" : {}}}, "?desc" : {"?algo" : (self.run_desc, "create_computer.txt"), "?non_args" : 2}},
            "try_del_computer" : {"?desc" : {"?algo" : (self.run_desc, "try_del_computer.txt"), "?non_args" : 2}},
            "force_del_computer" : {"?desc" : {"?algo" : (self.run_desc, "force_del_computer.txt"), "?non_args" : 2}},
            "rename_computer" : {"?desc" : {"?algo" : (self.run_desc, "rename_computer.txt"), "?non_args" : 2}},
            "edit_computer_resources" : {"?desc" : {"?algo" : (self.run_desc, "edit_computer_resources.txt"), "?non_args" : 2}},
            "get_cluster_programs" : {"?algo" : (self.get_cluster_programs, ), "?desc" : {"?algo" : (self.run_desc, "get_cluster_programs.txt"), "?non_args" : 2}},
            "get_cluster_instances" : {"?algo" : (self.get_cluster_instances, ), "?desc" : {"?algo" : (self.run_desc, "get_cluster_instances.txt"), "?non_args" : 2}},
            "start_program" : {"<program name" : {"<instance count?" : {"<req cores?" : {"<req memory?" : {}}}}, "?desc" : {"?algo" : (self.run_desc, "start_program.txt"), "?non_args" : 2}},
            "kill_program" : {"?desc" : {"?algo" : (self.run_desc, "kill_program.txt"), "?non_args" : 2}},
            "stop_program" : {"?desc" : {"?algo" : (self.run_desc, "stop_program.txt"), "?non_args" : 2}},
            "edit_program_resources" : {"?desc" : {"?algo" : (self.run_desc, "edit_program_resources.txt"), "?non_args" : 2}},
            "edit_process_resources" : {"?desc" : {"?algo" : (self.run_desc, "edit_process_resources.txt"), "?non_args" : 2}},
            "rename_program" : {"?desc" : {"?algo" : (self.run_desc, "rename_program.txt"), "?non_args" : 2}},
            "add_instance_gen_id" : {"?desc" : {"?algo" : (self.run_desc, "add_instance_gen_id.txt"), "?non_args" : 2}},
            "add_instance_user_id" : {"?desc" : {"?algo" : (self.run_desc, "add_instance_user_id.txt"), "?non_args" : 2}},
            "edit_instance_status" : {"?desc" : {"?algo" : (self.run_desc, "edit_instance_status.txt"), "?non_args" : 2}},
            "kill_instance" : {"?desc" : {"?algo" : (self.run_desc, "kill_instance.txt"), "?non_args" : 2}},
            "change_instance_id_gen" : {"?desc" : {"?algo" : (self.run_desc, "change_instance_id_gen.txt"), "?non_args" : 2}},
            "change_instance_id_user" : {"?desc" : {"?algo" : (self.run_desc, "change_instance_id_user.txt"), "?non_args" : 2}},
            "cleanup_cluster" : {"?desc" : {"?algo" : (self.run_desc, "cleanup_cluster.txt"), "?non_args" : 2}}
            
        }
        
        self.computer_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}},
                "?desc" : {"?algo" : (self.run_desc, "select.txt"), "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "save_amount" : {"<Name" : {"<How far back?": {"?algo" : (self.save_prev, )}}, "?desc" : {"?algo" : (self.run_desc, "save_amount.txt"), "?non_args" : 2}},
            "save_all" : {"<Name" : {"?algo" : (self.save_prev, "?replace", "all")}, "?desc" : {"?algo" : (self.run_desc, "save_all.txt"), "?non_args" : 2}},
            "reload" : {"?algo" : (self.reload, ), "?desc" : {"?algo" : (self.run_desc, "reload.txt"), "?non_args" : 2}},
            "update_commands" : {"?algo" : (self.update_dicts, ), "?desc" : {"?algo" : (self.run_desc, "update_commands.txt"), "?non_args" : 2}},
            "run" : {"?desc" : {"?algo" : (self.run_desc, "run.txt"), "?non_args" : 2}},
            "cleanup_computer" : {"?desc" : {"?algo" : (self.run_desc, "cleanup_computer.txt"), "?non_args" : 2}}
        }
        
        self.noMode_commands : dict = {
            "select" : {
                "root" : {"?algo" : (self.select_root, )},
                "cluster" : {},
                "computer" : {"?non_args" : 1},
                "run_folder" : {"<folder name" : {"?algo" : (self.select_run_folder, )}, "?non_args" : 2},
                "?desc" : {"?algo" : (self.run_desc, "select.txt"), "?non_args" : 2}
            },
            "exit" : {"?algo" : (self.exit, )},
            "save_amount" : {"<Name" : {"<How far back?": {"?algo" : (self.save_prev, )}}, "?desc" : {"?algo" : (self.run_desc, "save_amount.txt"), "?non_args" : 2}},
            "save_all" : {"<Name" : {"?algo" : (self.save_prev, "?replace", "all")}, "?desc" : {"?algo" : (self.run_desc, "save_all.txt"), "?non_args" : 2}},
            "reload" : {"?algo" : (self.reload, ), "?desc" : {"?algo" : (self.run_desc, "reload.txt"), "?non_args" : 2}},
            "update_commands" : {"?algo" : (self.update_dicts, ), "?desc" : {"?algo" : (self.run_desc, "update_commands.txt"), "?non_args" : 2}},
            "run" : {"?desc" : {"?algo" : (self.run_desc, "run.txt"), "?non_args" : 2}}
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
                
                self.cluster_commands["edit_instance_status"].update({f"{instance}" : {"true" : {"?algo" : (self.current_cluster.edit_instance_status, )}, 
                                                                                       "false" : {"?algo" : (self.current_cluster.edit_instance_status, )}}})
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
                        
                        if program in clusters[origin_cluster].programs.keys():
                    
                            self.root_commands["relocate_program"][f"{program}"].update({f"{origin_cluster}" : {}})
                            
                            for destination_cluster in clusters.keys():
                                
                                if destination_cluster == origin_cluster: continue
                                
                                self.root_commands["relocate_program"][f"{program}"][f"{origin_cluster}"].update({f"{destination_cluster}" : {"?algo" : (self.current_root.relocate_program, )}})
                    
                for computers in clusters[cluster].computers.keys():
                    
                    if computers:
                    
                        self.cluster_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.noMode_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.computer_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        self.root_commands["select"]["computer"][f"{cluster}"].update({f"{computers}" : {"?value" : clusters[cluster].computers[computers], "?algo" : (self.select_computer, )}, "?value" : clusters[cluster]})
                        
                        self.root_commands["move_computer"].update({f"{computers}" : {}})
                        
                        for origin_cluster in clusters.keys():
                            
                            if computers in clusters[origin_cluster].computers.keys():
                            
                                self.root_commands["move_computer"][f"{computers}"].update({origin_cluster : {}})
                            
                                for destination_cluster in clusters.keys():
                                    
                                    if destination_cluster == origin_cluster: continue
                                    
                                    self.root_commands["move_computer"][f"{computers}"][f"{origin_cluster}"].update({destination_cluster : {"?algo" : (self.current_root.move_computer, )}})
                                
                self.root_commands["try_del_cluster"].update({f"{cluster}" : {"?algo" : (self.current_root.delete_cluster, "?replace", "try")}})
                self.root_commands["force_del_cluster"].update({f"{cluster}" : {"?algo" : (self.current_root.delete_cluster, "?replace", "f")}})
                self.root_commands["rename_cluster"].update({f"{cluster}" : {"<New name" : {"?algo" : (self.current_root.rename_cluster, )}}})
      
        if self.folder:
            
            if Path.exists(self.folder):
            
                files = os.listdir(self.folder)
                
                for text_file in files:
                    
                    self.noMode_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                    self.computer_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                    self.root_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})
                    self.cluster_commands["run"].update({f"{text_file.split(".")[0]}" : {"?algo" : (self.read_file, ), "?value": f"{text_file}"}})


    def add_root(self):

        return input("Give the path to the root folder: ")
    
    def save_prev(self, name, amount):
        
        save_prev_coms = []
        
        if amount == "all":
            for item in self.previous_commands:
                save_prev_coms.append(item + "\n")
        else:
            if len(self.previous_commands) > amount + 1:
                for item in self.previous_commands[:amount + 1]:
                    save_prev_coms.append(item + "\n")
        
        save_prev_coms = save_prev_coms[1:]
        if len(save_prev_coms) > 0:
            save_prev_coms.reverse()
            
            with open(Path.join(self.folder, name + ".txt"), "w") as f:
                
                f.writelines(save_prev_coms)
                f.close()
        else:
            
            print("Something went wrong")
                
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
        """Can't run in Vscode terminal, breaks"""
        
        os.execv(sys.executable, ['python'] + sys.argv)
        
    def run_desc(self, file_name):
        """Print out the description of the commands"""
        
        with open(Path.join(self.desc_folder, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            f.close()
            
        print(content)
        input("Press enter to continue")

    def exit(self):

        sys.stdout.flush()  # Flush output buffer
        sys.exit()  # Terminate the program