import shutil
import re
import os
from os import path as Path
from datetime import datetime
from colorama import Fore, Style, Back

class Computer:
    def __init__(self, path: str):
        path: str = Path.normpath(fr"{path}")
        computer_name: str = path.split(os.sep)[-1]
        self.name: str = computer_name

        if Path.exists(Path.join(path, ".szamitogep_config")):
            config_file = open(Path.join(path, ".szamitogep_config"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            if len(config) != 2:
                self.print(f"{Fore.RED}Invalid configuration file at path: {path}")
                return
            
            cores: int = int(config[0])
            memory: int = int(config[1])

            self.cores: int = cores
            self.memory: int = memory
            
            self.path: str = path

            if not self.validate_computer(): return
            self.cleanup()
            self.print(f"{Back.GREEN}{Fore.BLACK}Computer ({computer_name}) initialized with {cores} cores and {memory} of memory. {self.free_cores} cores and {self.free_memory} memory left free.{Back.RESET}\n\n")

        else:
            self.print(f"{Fore.RED}There's no config file in {path}")
            return


    def validate_computer(self) -> bool:
        # self.cleanup()
        usage: dict = self.calculate_resource_usage()

        if usage["memory_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
            return False
        
        if usage["core_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Core limit exceeded ({usage["core_usage_percent"]}%).")
            return False
        
        return True


    def calculate_resource_usage(self) -> dict:
        prog_instances: dict = self.get_prog_instances()

        memory_usage: int = 0
        cpu_usage: int = 0

        for _, info in prog_instances.items():
            if info["status"]:
                memory_usage += int(info["memory"])
                cpu_usage += int(info["cores"])

        self.free_memory: int = self.memory - memory_usage
        self.free_cores: int = self.cores - cpu_usage

        memory_usage_percentage: float = round(memory_usage / self.memory * 100, 1)
        cpu_usage_percentage: float = round(cpu_usage / self.cores * 100, 1)

        return {"memory_usage_percent": memory_usage_percentage, "core_usage_percent": cpu_usage_percentage}

    """
        Ok cro pussoltam es itt volt egy merge conflict ahelyett hogy kitalalom hogy itt mi a jo (gondolom a get processes mar nem kell), rad hagyom balls
    """

    def get_processes(self) -> dict:
        """Gives back all the running processes on the computer"""
        files: list = os.listdir(self.path)
        process_list: dict = {}

        if ".szamitogep_config" in files:
            files.remove(".szamitogep_config")

        for process in files:
            try:
                process_list[process] = self.get_process_info(process)
            except:
                self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: process ({process}) is incorrect.")

        return process_list
    
    def get_prog_instances(self) -> dict:
        """Return only valid instances"""
        files = os.listdir(self.path)
        valid_instances = {}
        
        for f in files:
            full_path = Path.join(self.path, f)
            if self.is_prog_instance_file(full_path):
                details = self.get_prog_instance_info(f)
                if details:
                    valid_instances[f] = details
        return valid_instances


    def get_prog_instance_info(self, filename: str) -> dict:
        """Returns None instead of erroring on invalid instances"""
        try:
            if not self.is_prog_instance_file(Path.join(self.path, filename)):
                return None
                
            name_part, instance_id = filename.split("-")
            with open(Path.join(self.path, filename), "r") as f:
                lines = [line.strip() for line in f.readlines()]
                
            return {
                "name": name_part,
                "id": instance_id,
                "status": lines[1] == "AKTÍV",
                "cores": int(lines[2]),
                "memory": int(lines[3]),
                "date_started": lines[0]
            }
        except:
            return None

    def is_prog_instance_file(self, path: str) -> bool:
        filename = Path.basename(path)
        
        # Check filename format: programname-id (id must be 6 chars)
        if not re.match(r"^[a-zA-Z0-9]+-[a-zA-Z0-9]{6}$", filename):
            return False
        
        # Check file contents structure
        try:
            with open(path, "r", encoding="utf8") as file:
                lines = [line.strip() for line in file.readlines()]
            
            return (len(lines) == 4 and
                    re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", lines[0]) and
                    lines[1] in {"AKTÍV", "INAKTÍV"} and
                    lines[2].isdigit() and 
                    lines[3].isdigit())
        except:
            return False

    def edit_instance(self, instance_id: str, property_name: str, new_value: str) -> bool:
        """Edit an existing instance file"""
        instance_path = Path.join(self.path, instance_id)
        
        if not self.is_prog_instance_file(instance_path):
            return False

        try:
            with open(instance_path, "r+", encoding="utf8") as f:
                lines = [line.strip() for line in f.readlines()]
                
                # Map properties to line numbers
                property_map = {
                    "status": 1,
                    "cores": 2,
                    "memory": 3
                }
                
                if property_name not in property_map:
                    return False
                
                # Update the value
                line_idx = property_map[property_name]
                lines[line_idx] = str(new_value).upper() if property_name == "status" else str(new_value)
                
                # Write back changes
                f.seek(0)
                f.truncate()
                f.write("\n".join(lines))
            
            return True
        except Exception as e:
            self.print(f"Failed to edit instance {instance_id}: {str(e)}")
            return False

#MISC.
    def cleanup(self) -> bool:
        """Removes unnecessary files and directories from the computer"""
        
        files: list = os.listdir(self.path)
        removed_files: int = 0

        self.print(f"{Fore.GREEN}Starting cleanup...")

        if Path.exists(Path.join(self.path, ".szamitogep_config")):
            files.remove(".szamitogep_config")

        for file in files:
            target_path = Path.join(self.path, file)

            if self.is_prog_instance_file(target_path):
                continue

            while True:
                try:
                    user_input = input(
                        f"Unidentified file detected in {self.name}: {file}\n"
                        "1: Delete\n"
                        "2: Keep (Warning: Might make the computer unstable)\n"
                        "Enter your choice (1/2): "
                    ).strip()

                    if user_input == "1":
                        try:
                            if Path.isfile(target_path):
                                self.print(f"Removing file ({file}).")
                                os.remove(target_path)
                            else:
                                self.print(f"Removing folder ({file}).")
                                shutil.rmtree(target_path)
                            removed_files += 1
                        except Exception as e:
                            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR: Cannot delete ({file}). {e}")
                        break  # Exit the while loop after action
                    elif user_input == "2":
                        self.print(f"Skipping file ({file}).")
                        break  # Exit the while loop after action
                    else:
                        self.print("Invalid input. Please enter 1 or 2.")

                except KeyboardInterrupt:
                    self.print(f"\n{Fore.RED}Cleanup interrupted by user.{Fore.RESET}")
                    return False

        self.print(f"{Fore.GREEN}Cleanup completed. Removed {removed_files} files/folders.")
        return True

    
    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Style.BRIGHT}{Fore.CYAN}[{Fore.WHITE}{self.name}{Fore.CYAN}]: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)