import os
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style, Back
from modules.rebalancer import *

global_processes : dict = {}
global_active_processes : dict = {}
global_inactive_processes : dict = {}

class Cluster:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")
        self.path: str = path
        cluster_name: str = path.split(os.sep)[-1]
        self.name : str = cluster_name

        if Path.exists(Path.join(path, ".klaszter")):
            config_file = open(Path.join(path, ".klaszter"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            for line in config:
                config[config.index(line)] = line.strip()

            app_list: list = []
            instance_count_list: list = []
            cores_list: list = []
            memory_list: list = []

            process_info_dict: dict = {}

            for app in config[0::4]:
                app_list.append(app)

            for instance_count in config[1::4]:
                instance_count_list.append(instance_count)

            for cores in config[2::4]:
                cores_list.append(cores)
            
            for memory in config[3::4]:
                memory_list.append(memory)

            for i, app in enumerate(app_list):
                process_info_dict[app] = {"instance_count": instance_count_list[i], "cores": cores_list[i], "memory": memory_list[i], "running": True, "date_started" : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            self.processes: dict = process_info_dict
            
            self.active_processes : dict = {}
            self.inactive_processes : dict = {}
            
            self.__sort_processes()
            self.format_cluster_config()
            self.update_cluster_config()

        else:
            self.print(f"{Style.BRIGHT + Fore.RED}Cluster {cluster_name} doesn`t have a config file")
            self.print(f"{Style.BRIGHT + Fore.GREEN}Creating .klaszter file now")

            new_cluster_file = open(Path.join(self.path, ".klaszter"), "w", encoding="utf-8", )
            new_cluster_file.write("")
            new_cluster_file.close()

            self.__init__(self.path)
            return

        
        files: list = os.listdir(path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        self.cleanup()

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(path, file))
        
        self.computers : dict = computer_dict
        self.rebalancer : Rebalancer = Rebalancer(self.path, self)
        
        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({cluster_name}) initialized succesfully with {len(computer_dict)} computer(s).{Back.RESET+Fore.RESET}\n")
        self.initialized : bool = True

    #Save processes them into global process and group to active and inactive
    def __sort_processes(self) -> None:
        self.active_processes.clear()
        self.inactive_processes.clear()

        for name in self.processes:
            if name not in global_processes:  # Ensure process is added globally
                global_processes[name] = self.processes[name]

        for name in global_processes:
            if global_processes[name]["running"] == True:
                if name not in global_active_processes:
                    global_active_processes[name] = global_processes[name]
                self.active_processes = global_active_processes.copy()
            else:
                if name not in global_inactive_processes:
                    global_inactive_processes[name] = global_processes[name]
                self.inactive_processes = global_inactive_processes.copy()

    #Clear the .klaszter file so we can rewrite it
    def format_cluster_config(self) -> None:
        with open(Path.join(self.path, ".klaszter"), "w", encoding="utf8") as config_file:
            config_file.write("")
        config_file.close()


    def update_cluster_config(self) -> None:
        for name in self.active_processes:
            data: str = f"{name}\n{self.active_processes[name]["instance_count"]}\n{self.active_processes[name]["cores"]}\n{self.active_processes[name]["memory"]}\n"

            with open(Path.join(self.path, ".klaszter"), "a", encoding="utf8") as file:
                file.write(data)
            file.close()

    # Group tasks update processes, clean the config, and reinitialize the cluster
    def __update_cluster_state(self):
        self.__sort_processes()
        self.format_cluster_config()
        self.update_cluster_config()
        self.__init__(self.path)


    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        path: str = Path.join(self.path, computer_name)

        if Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(path)
            config_file = open(Path.join(path, ".szamitogep_config"), "w", encoding="utf8")
            config_file.write(f"{cores}\n{memory}")
            config_file.close()

            self.print(f"{Fore.GREEN}Computer ({computer_name}) created successfully.")
            
            self.__init__(self.path)
            return Computer(path)   
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            self.__init__(self.path)
            return
        
    # Only works if there are no processes running under the computer
    def try_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        try:
            computer: Computer = Computer(path)
            if computer.get_processes():
                self.print(f"{Fore.RED}Unable to delete computer '{computer_name}'. It has processes, try using force_delete_computer().")
                self.__init__(self.path)
                return False
            
            os.remove(Path.join(path, ".szamitogep_config"))
            os.rmdir(path)

            self.print(f"{Fore.GREEN}Computer '{computer_name}' deleted successfully.")
            self.__init__(self.path)
            return True
        except:
            self.print(f"{Fore.RED}Unable to delete computer ({computer_name}).")
            self.__init__(self.path)
            return False


    def force_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        try:
            for file in os.listdir(path):
                os.remove(Path.join(path, file))

            os.rmdir(path)
            self.print(f"{Fore.GREEN}Successfully force deleted computer ({computer_name}).")
            self.__init__(self.path)
            return True
        except:
            self.print(f"{Back.RED}{Fore.BLACK}CRITICAL ERROR DETECTED: force deletion failed for computer {computer_name}.")
            self.__init__(self.path)
            return False

    # TODO : Move this function into the ROOT class
    def rename_cluster(self, new_name : str) -> bool:
        if not self.initialized:
            self.print(f"{Fore.RED}Cluster failed to initialize so renaming can't be done. New cluster name would be: {new_name}.")
            return False
        
        try:
            parent_dir: str = Path.dirname(self.path)
            new_path: str = Path.join(parent_dir, new_name)

            if Path.exists(new_path):
                self.print(f"{Fore.RED}Renaming failed. There is already a cluster called {new_name}.")
                return False

            os.rename(self.path, new_path)
            self.path = new_path
            self.print(f"{Fore.GREEN}Cluster folder renamed to '{new_name}' successfully.")

            self.__init__(self.path)
            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming cluster: {e}")
            return False
        
    
    def rename_computer(self, computer_name : str, new_name : str) -> bool:
        if not self.initialized:
            self.print(f"{Fore.RED}Cluster failed to initialize so renaming can't be done.")
            return False
        
        try:
            computer_dir: str = Path.join(self.path, computer_name)
            
            if not Path.exists(computer_dir):
                self.print(f"{Fore.RED}A computer with the name {computer_dir} does not exist.")
                return False
            
            new_path: str = Path.join(self.path, new_name)

            os.rename(computer_dir, new_path)
            self.print(f"{Fore.GREEN}Computer folder renamed to '{new_name}' successfully.")

            self.__init__(self.path)
            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming computer: {e}")
            return False

    # Explanation docs.txt
    def start_process(self, process_name: str, running: bool, cpu_req: int, ram_req: int, instance_count: int = 1, date_started: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')) -> bool:
        if process_name in global_processes:
            self.print(f"{Fore.RED}{process_name} is already a process on the cluster. Maybe try another name.")
            return False

        try:
            # Add process to global_processes first
            global_processes[process_name] = {
                "instance_count": instance_count,
                "cores": cpu_req,
                "memory": ram_req,
                "running": running,
                "date_started": date_started
            }
            
            # Ensure local process list is also updated before reinitializing
            self.processes[process_name] = global_processes[process_name]
            self.__sort_processes()  # Resort after adding a new process
            self.format_cluster_config()
            self.update_cluster_config()

            self.print(f"{Fore.GREEN}Process ({process_name}) added successfully to cluster ({self.name}) as {"AKTIV" if running else f"{Fore.YELLOW + Style.BRIGHT}INAKTIV"}.")

            self.__init__(self.path)  # Reinitialize after ensuring all updates
            return True

        except Exception as e:
            self.print(f"{Fore.RED}Error while creating process: {process_name} -> {e}")
            return False

    # Explanation docs.txt
    def kill_process(self, process_name: str) -> bool:
        try:
            self.print(f"{Style.BRIGHT}Attempting to kill process: {process_name}")

            # Check if process exists in global processes
            if process_name in global_processes:
                del self.processes[process_name]
                del global_processes[process_name]

                global_active_processes.pop(process_name, None)
                global_inactive_processes.pop(process_name, None)

                # Resort, clean, and update
                self.__update_cluster_state()

                self.print(f"{Style.BRIGHT}Process {process_name} successfully killed.")
                return True
            
            self.print(f"{Fore.RED}Error: Process {process_name} does not exist in global_processes!")
            return False
        except Exception as e:
            self.print(f"{Fore.RED}Error while killing process {process_name}: {e}")
            return False


    def edit_process_resources(self, process_name: str, property_to_change : str, new_value) -> bool:
        try:
            if process_name not in global_processes:
                self.print(f"{Fore.RED}Process {process_name} does not exist! Check the name and try again.")
                return False
            
            allowed_properties = ["instance_count", "cores", "memory", "running"]
            
            if property_to_change not in allowed_properties:
                self.print(f"{Fore.RED}Invalid property. Allowed: {allowed_properties}")
                return False

            # Convert new_value to correct type
            if property_to_change in ["instance_count", "cores", "memory"]:
                new_value = int(new_value)
            elif property_to_change == "running":
                new_value = bool(new_value)

            # Apply changes
            global_processes[process_name][property_to_change] = new_value
            self.processes[process_name][property_to_change] = new_value

            # Update cluster
            self.__update_cluster_state()

            self.print(f"{Fore.GREEN}Updated process ({process_name}): {property_to_change} -> {new_value}")
            return True

        except Exception as e:
            self.print(f"{Fore.RED}Error while editing process {process_name}: {e}")
            return False


    def rename_process(self, process_name: str, new_process_name: str) -> bool:
        try:
            # Ensure the process exists
            if process_name not in global_processes:
                self.print(f"{Fore.RED}Process {process_name} does not exist! Check the name and try again.")
                return False

            # Ensure the new name is not already taken
            if new_process_name in global_processes:
                self.print(f"{Fore.RED}A process with the name {new_process_name} already exists!")
                return False

            # Move the process to the new name
            global_processes[new_process_name] = global_processes.pop(process_name)
            self.processes[new_process_name] = self.processes.pop(process_name)

            # Update active/inactive process lists
            if process_name in global_active_processes:
                global_active_processes[new_process_name] = global_active_processes.pop(process_name)
            elif process_name in global_inactive_processes:
                global_inactive_processes[new_process_name] = global_inactive_processes.pop(process_name)

            # Resort processes and update cluster config
            self.__update_cluster_state()

            self.print(f"{Fore.GREEN}Process {process_name} successfully renamed to {new_process_name}.")
            return True

        except Exception as e:
            self.print(f"{Fore.RED}Error while renaming process {process_name}: {e}")
            return False

    # Removes unnescecary files and directories from the cluster
    def cleanup(self) -> bool:
        files: list = os.listdir(self.path)
        
        self.print(f"{Fore.GREEN}Starting cleanup...")

        if Path.exists(Path.join(self.path, ".klaszter")):
            files.remove(".klaszter")

        removed_files : int = 0

        for file in files:
            if Path.exists(Path.join(self.path, file, ".szamitogep_config")):
                continue
            
            try:
                if Path.isdir(Path.join(self.path, file)):
                    os.rmdir(Path.join(self.path, file))
                else:
                    os.remove(Path.join(self.path, file))
                self.print(f"{Fore.YELLOW}Removed {file} from filesystem since it was marked as incorrect. ")
            except:
                pass
        
        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True
    
    # Only for debugging purposes
    def print(self, text: str):
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)