import shutil
import os
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style, Back
from modules.rebalancer import *
from datetime import datetime

rebalancing_algos : list = ["load_balance", "best_fit", "fast"]

class Cluster:
    def __init__(self, path: str):
        if not hasattr(self, '_cluster_initialized'):
            # Unique to THIS SPECIFIC INSTANCE
            self._cluster_initialized = True
            self.default_rebalance_algo = rebalancing_algos[1]
            self._saved_processes = {}
            self._saved_active_processes = {}
            self._saved_inactive_processes = {}

        # Always process config but preserve state
        self.path = Path.normpath(fr"{path}")
        self.name = self.path.split(os.sep)[-1]
        self.rebalancer : Rebalancer = Rebalancer(self.path, self)

        self.restart_cluster()

 
        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({self.name}) initialized succesfully with {len(self.computers)} computer(s).{Back.RESET+Fore.RESET}\n")
        self.initialized : bool = True
        self._saved_processes.keys()


#Cluster
    def _load_config(self):
        """Load/reload config file without resetting saved processes"""
        if Path.exists(Path.join(self.path, ".klaszter")):
            config_file = open(Path.join(self.path, ".klaszter"), "r", encoding="utf8")
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

            self.active_processes : dict = {}
            self.inactive_processes : dict = {}

            self.processes : dict = process_info_dict
            self.__sort_processes()
            self.format_cluster_config()
            self.update_cluster_config()

            # self.rebalancer.distribute_processes_balanced()

            return

        else:
            self.print(f"{Style.BRIGHT + Fore.RED}Cluster {self.name} doesn`t have a config file")
            self.print(f"{Style.BRIGHT + Fore.GREEN}Creating .klaszter file now")

            new_cluster_file = open(Path.join(self.path, ".klaszter"), "w", encoding="utf-8", )
            new_cluster_file.write("")
            new_cluster_file.close()

            self._load_config()
            self.cleanup()
            self._load_computers()

            # self.rebalancer.distribute_processes_balanced()
            return


    def _load_computers(self):
        files: list = os.listdir(self.path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(self.path, file))
        
        self.computers : dict = computer_dict


    def restart_cluster(self):
        self._load_config()
        self.cleanup()
        self._load_computers()
        self.run_default_rebalance_algo()


    def __sort_processes(self) -> None:
        # Merge .klaszter processes into saved processes
        for name, details in self.processes.items():
            self._saved_processes[name] = details

        # Update active/inactive from ALL saved processes
        self._saved_active_processes.clear()
        self._saved_inactive_processes.clear()
        
        for name, details in self._saved_processes.items():
            if details["running"]:
                self._saved_active_processes[name] = details
            else:
                self._saved_inactive_processes[name] = details

        # Update public-facing views
        self.active_processes = self._saved_active_processes.copy()
        self.inactive_processes = self._saved_inactive_processes.copy()


    def set_default_rebalance_algo(self, new_algo_name : str) -> bool:
        if not new_algo_name in rebalancing_algos:
            self.print(f"{Fore.RED}There is no rebalancing algorithm called {new_algo_name}.")
            return False

        old_algo_name = self.rebalancer.default_rebalance_algo

        self.rebalancer.default_rebalance_algo = new_algo_name
        
        self.print(f"{Fore.GREEN}Succesfully changed the default rebalancing algorithm from {Fore.YELLOW + Style.BRIGHT}{old_algo_name}{Fore.GREEN + Style.RESET_ALL} to {Fore.YELLOW + Style.BRIGHT}{new_algo_name}")
        return True


    def run_default_rebalance_algo(self):
        self.rebalancer.run_default_rebalance_algo()

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
        """Update config file without full reinitialization"""
        self.__sort_processes()
        self.format_cluster_config()
        self.update_cluster_config()
        self._load_config()  # Reload from updated file


#Computers
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
            
            self.restart_cluster()
            return Computer(path)   
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            self.restart_cluster()
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
                return False
            
            os.remove(Path.join(path, ".szamitogep_config"))
            os.rmdir(path)

            self.print(f"{Fore.GREEN}Computer '{computer_name}' deleted successfully.")
            self.restart_cluster()

            return True
        except:
            self.print(f"{Fore.RED}Unable to delete computer ({computer_name}).")
            self.restart_cluster()

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
            self.restart_cluster()

            return True
        except:
            self.print(f"{Back.RED}{Fore.BLACK}CRITICAL ERROR DETECTED: force deletion failed for computer {computer_name}.")
            self.restart_cluster()

            return False
        

    def edit_computer_resources(self, computer_name: str, cores: int, memory: int) -> bool:
        computer : Computer = self.computers[computer_name]    
        
        min_cores: int = computer.cores - computer.free_cores
        min_memory: int = computer.memory - computer.free_memory

        if cores < min_cores:
            self.print(f"{Fore.RED}Can't set core count to {cores} on computer ({computer.name}). Required minimum cores: {min_cores} ")
            return False
            
        if memory < min_memory:
            self.print(f"{Fore.RED}Can't set memory size to {memory} on computer ({computer.name}). Required minimum memory size: {min_memory} ")
            return False

        prev_cores: int = computer.cores
        prev_memory: int = computer.memory

        computer.cores = cores
        computer.memory = memory
            
        if computer.validate_computer():
            computer.calculate_resource_usage()

            with open(Path.join(computer.path, ".szamitogep_config"), "w", encoding="utf-8") as file:
                file.write(f"{computer.cores}\n{computer.memory}")
            file.close()

            self.restart_cluster()
            self.print(f"{Fore.GREEN}Succesfully edited resources on computer ({computer.name}). Memory: {prev_memory} -> {memory}, cores: {prev_cores} -> {cores}")


            return True
        
        else:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't validate computer ({computer.name}). Setting back previus resources.")
            computer.cores = prev_cores
            computer.memory = memory
            computer.calculate_resource_usage()
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

            self.restart_cluster()

            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming computer: {e}")
            return False


#Processes
    def start_process(self, process_name: str, running: bool, cpu_req: int, ram_req: int, instance_count: int = 1, date_started: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')) -> bool:
        if process_name in self._saved_processes:
            self.print(f"{Fore.RED}{process_name} already exists")
            return False

        try:
            # Update instance's saved processes
            self._saved_processes[process_name] = {
                "instance_count": instance_count,
                "cores": cpu_req,
                "memory": ram_req,
                "running": running,
                "date_started": date_started
            }
            
            # Update config file
            self.__update_cluster_state()

            self.print(f"{Fore.GREEN}Process ({process_name}) added successfully to cluster ({self.name}) as {"AKTIV" if running else f"{Fore.YELLOW + Style.BRIGHT}INAKTIV"}.")
            return True
        
        except Exception as e:
            self.print(f"{Fore.RED}Error while creating process: {process_name} -> {e}")
            return False

        # Explanation docs.txt
    
    
    def kill_process(self, process_name: str) -> bool:
        try:
            if process_name in self._saved_processes:
                del self.processes[process_name]
                del self._saved_processes[process_name]
                self._saved_active_processes.pop(process_name, None)
                self._saved_inactive_processes.pop(process_name, None)

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
            if process_name not in self._saved_processes:
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
            self._saved_processes[process_name][property_to_change] = new_value
        
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
            if process_name not in self._saved_processes:
                self.print(f"{Fore.RED}Process {process_name} does not exist! Check the name and try again.")
                return False

            # Ensure the new name is not already taken
            if new_process_name in self._saved_processes:
                self.print(f"{Fore.RED}A process with the name {new_process_name} already exists!")
                return False

            # Move the process to the new name
            self._saved_processes[new_process_name] = self._saved_processes.pop(process_name)
            self.processes[new_process_name] = self.processes.pop(process_name)

            # Update active/inactive process lists
            if process_name in self._saved_active_processes:
                self._saved_active_processes[new_process_name] = self._saved_active_processes.pop(process_name)
            elif process_name in self._saved_inactive_processes:
                self._saved_inactive_processes[new_process_name] = self._saved_inactive_processes.pop(process_name)

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
                target_path = Path.join(self.path, file)
                
                if Path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)

                self.print(f"{Fore.YELLOW}Removed {file} from filesystem since it was marked as incorrect.")
            except:
                self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Cluster might be unstable.")
                return False
        
        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True

    # Only for debugging purposes
    def print(self, text: str):
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)